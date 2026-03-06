"""안전한 코드 실행 엔진.

사용자 코드를 subprocess로 격리 실행하고,
AST 보안 검증 -> 프로세스 격리 -> 리소스 제한의 파이프라인을 거친다.

실행 파이프라인:
    1. SecurityValidator: AST 정적 분석으로 위험 패턴 차단
    2. MemorySafetyValidator: 리소스 남용 패턴 차단
    3. _build_execution_script: 샌드박스 래퍼가 포함된 실행 스크립트 생성
    4. subprocess.run: 별도 프로세스에서 격리 실행 (타임아웃 제한)
    5. _parse_result: 실행 결과 파싱 및 변수 추출

보안 계층:
    - 1단계 (정적): AST 분석으로 위험 코드 사전 차단
    - 2단계 (런타임): exec() globals 스코프에서 위험 함수 차단
    - 3단계 (프로세스): subprocess 격리로 호스트 시스템 보호
    - 4단계 (리소스): 타임아웃과 출력 크기 제한
"""

import base64
import json
import os
import re
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from io import StringIO
from typing import Optional

from core.security import MemorySafetyValidator, SecurityValidator


@dataclass
class ExecutionResult:
    """코드 실행 결과를 담는 데이터 클래스.

    Attributes:
        stdout: 표준 출력 내용
        stderr: 표준 에러 내용
        variables: 실행 후 추출된 사용자 변수 딕셔너리
        success: 실행 성공 여부
        error_type: 에러 발생 시 에러 클래스 이름 (예: "NameError")
        error_line: 에러 발생 줄 번호
        execution_time: 실행 시간 (초)
    """

    stdout: str = ""
    stderr: str = ""
    variables: dict = field(default_factory=dict)
    success: bool = True
    error_type: Optional[str] = None
    error_line: Optional[int] = None
    execution_time: float = 0.0


class VirtualFileSystem:
    """메모리 기반 가상 파일시스템.

    Ch6(파일 입출력) 학습에서 실제 파일시스템 대신 사용하는
    인메모리 파일시스템이다. open(), read(), write() 등의
    파일 연산을 메모리 상에서 시뮬레이션한다.

    Attributes:
        files: 가상 파일 저장소 {파일명: 내용}
        _open_files: 열려 있는 파일 객체 추적 리스트

    Examples:
        >>> vfs = VirtualFileSystem({"data.txt": "hello\\nworld"})
        >>> f = vfs.open("data.txt", "r")
        >>> f.read()
        'hello\\nworld'
    """

    def __init__(self, preset_files: Optional[dict] = None) -> None:
        """VirtualFileSystem 초기화.

        Args:
            preset_files: 미리 생성할 가상 파일 딕셔너리 {파일명: 내용}
        """
        self.files: dict[str, str] = dict(preset_files or {})
        self._open_files: list = []

    def open(self, filename: str, mode: str = "r") -> StringIO:
        """가상 파일을 열어 파일 객체를 반환한다.

        Args:
            filename: 열 파일 이름
            mode: 파일 열기 모드 ("r", "w", "a" 지원)

        Returns:
            파일 객체 (read/write 가능)

        Raises:
            FileNotFoundError: "r" 모드에서 파일이 없을 때
            ValueError: 지원하지 않는 모드를 사용할 때
        """
        if mode == "r":
            if filename not in self.files:
                raise FileNotFoundError(
                    f"파일을 찾을 수 없습니다: '{filename}'"
                )
            stream = _VirtualFile(
                self, filename, mode, self.files[filename]
            )
            self._open_files.append(stream)
            return stream

        elif mode == "w":
            self.files[filename] = ""
            stream = _VirtualFile(self, filename, mode, "")
            self._open_files.append(stream)
            return stream

        elif mode == "a":
            existing = self.files.get(filename, "")
            stream = _VirtualFile(self, filename, mode, existing)
            self._open_files.append(stream)
            return stream

        else:
            raise ValueError(
                f"지원하지 않는 파일 모드입니다: '{mode}'. "
                f"'r', 'w', 'a'만 사용할 수 있습니다."
            )


class _VirtualFile(StringIO):
    """가상 파일 래퍼.

    StringIO를 상속하여 close() 시 VirtualFileSystem에
    내용을 자동으로 반영한다.
    """

    def __init__(
        self,
        vfs: VirtualFileSystem,
        filename: str,
        mode: str,
        initial_value: str,
    ) -> None:
        """_VirtualFile 초기화.

        Args:
            vfs: 소속 VirtualFileSystem
            filename: 파일 이름
            mode: 열기 모드
            initial_value: 초기 내용
        """
        super().__init__(initial_value)
        self._vfs = vfs
        self._filename = filename
        self._mode = mode

        # 추가 모드에서는 커서를 끝으로 이동
        if mode == "a":
            self.seek(0, 2)

    def close(self) -> None:
        """파일을 닫고 내용을 VFS에 반영한다."""
        if self._mode in ("w", "a"):
            self._vfs.files[self._filename] = self.getvalue()
        super().close()

    def __enter__(self):
        """with 문 진입 시 자기 자신을 반환한다."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 문 종료 시 파일을 닫는다."""
        self.close()
        return False


class CodeExecutor:
    """안전한 코드 실행기.

    사용자 코드를 AST 보안 검증 후 subprocess로 격리 실행한다.
    동시 실행 수 제한, 타임아웃, 출력 크기 제한 등
    다중 보안 계층을 통해 서비스 안정성을 보장한다.

    Attributes:
        timeout: 실행 타임아웃 (초)
        max_output: 최대 출력 크기 (바이트)
        chapter_id: 현재 학습 챕터 번호
        _security_validator: AST 보안 검증기
        _memory_validator: 메모리 안전성 검증기
        _semaphore: 동시 실행 제한 세마포어
    """

    # === 변수 추출 마커 ===
    # 사용자 코드 실행 후 로컬 변수를 stdout으로 전달할 때 사용하는 구분자
    _VARS_MARKER_START: str = "\n__METACODE_VARS__\n"
    _VARS_MARKER_END: str = "\n__METACODE_VARS_END__\n"

    def __init__(
        self,
        timeout: float = 5.0,
        max_output: int = 10240,
        chapter_id: int = 1,
    ) -> None:
        """CodeExecutor 초기화.

        Args:
            timeout: 코드 실행 최대 시간 (초). 기본값 5초.
            max_output: stdout/stderr 최대 크기 (바이트). 기본값 10KB.
            chapter_id: 현재 챕터 번호 (1~8).
        """
        self.timeout = timeout
        self.max_output = max_output
        self.chapter_id = chapter_id

        self._security_validator = SecurityValidator()
        self._memory_validator = MemorySafetyValidator()

        # 동시 실행 제한: 최대 3개의 코드가 병렬 실행 가능
        self._semaphore = threading.Semaphore(3)

    def execute(
        self,
        code: str,
        preset_inputs: Optional[list] = None,
        inject_variables: Optional[dict] = None,
    ) -> ExecutionResult:
        """사용자 코드를 안전하게 실행한다.

        실행 파이프라인:
            1. AST 보안 검증 (SecurityValidator + MemorySafetyValidator)
            2. 실행 스크립트 생성 (_build_execution_script)
            3. 임시 파일에 저장
            4. subprocess.run으로 격리 실행
            5. 결과 파싱 (_parse_result)
            6. 에러 발생 시 한국어 번역 (ErrorTranslator)

        Args:
            code: 실행할 Python 소스코드
            preset_inputs: input() 함수에 제공할 미리 정의된 입력 리스트
            inject_variables: 사용자 코드에 주입할 변수 딕셔너리

        Returns:
            ExecutionResult: 실행 결과
        """
        # === Step 1: AST 보안 검증 ===
        is_safe, security_msg = self._security_validator.validate(
            code, self.chapter_id
        )
        if not is_safe:
            return ExecutionResult(
                success=False,
                stderr=security_msg,
                error_type="SecurityError",
            )

        is_safe, memory_msg = self._memory_validator.validate(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                stderr=memory_msg,
                error_type="SecurityError",
            )

        # === Step 2: 실행 스크립트 생성 ===
        script = self._build_execution_script(
            code, preset_inputs, inject_variables
        )

        # === Step 3: 세마포어 획득 후 실행 ===
        acquired = self._semaphore.acquire(timeout=10.0)
        if not acquired:
            return ExecutionResult(
                success=False,
                stderr="서버가 바쁩니다. 잠시 후 다시 시도해 주세요.",
                error_type="ServerBusy",
            )

        tmp_file = None
        try:
            tmp_file = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            )
            tmp_file.write(script)
            tmp_file.close()

            # === Step 4: subprocess로 격리 실행 ===
            start_time = time.time()

            result = subprocess.run(
                ["python", "-u", tmp_file.name],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding="utf-8",
                errors="replace",
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )

            execution_time = time.time() - start_time

            stdout = result.stdout[: self.max_output]
            stderr = result.stderr[: self.max_output]

            # === Step 5: 결과 파싱 ===
            return self._parse_result(stdout, stderr, execution_time)

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                stderr=(
                    f"코드 실행 시간이 {self.timeout}초를 초과했습니다. "
                    f"무한 루프가 있는지 확인해 주세요."
                ),
                error_type="TimeoutError",
                execution_time=execution_time,
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=f"코드 실행 중 예기치 않은 오류: {str(e)}",
                error_type="InternalError",
            )

        finally:
            self._semaphore.release()
            if tmp_file and os.path.exists(tmp_file.name):
                try:
                    os.unlink(tmp_file.name)
                except OSError:
                    pass

    def _build_execution_script(
        self,
        code: str,
        preset_inputs: Optional[list] = None,
        inject_variables: Optional[dict] = None,
    ) -> str:
        """샌드박스 래퍼가 포함된 실행 스크립트를 생성한다.

        사용자 코드를 안전하게 감싸는 실행 스크립트를 문자열로 조립한다.
        순서:
            1. 인코딩 선언
            2. 시스템 모듈 사전 import (차단 전에 완료)
            3. input() 오버라이드
            4. 안전한 getattr 래퍼
            5. __import__ 차단/제한 (import depth 추적)
            6. 사용자 코드 실행 (builtins 스코프 격리)
            7. 변수 추출 (JSON 마커)

        Args:
            code: 사용자 코드
            preset_inputs: input()에 제공할 입력 리스트
            inject_variables: 주입할 변수 딕셔너리

        Returns:
            완전한 실행 스크립트 문자열
        """
        parts: list[str] = []

        # === 1. 인코딩 선언 ===
        parts.append("# -*- coding: utf-8 -*-")

        # === 2. 시스템 모듈/함수 사전 확보 ===
        # 모든 builtins 오버라이드 및 import 차단보다 먼저 수행한다.
        # 이유:
        #   - import 구문은 내부적으로 builtins.locals()를 호출함
        #   - class 정의(enum.py 등)는 builtins.type()의 3인자 호출 필요
        #   - numpy 등 내부 모듈이 exec/compile/open을 사용함
        parts.append(
            "# --- 시스템 모듈/함수 사전 확보 (모든 차단보다 먼저) ---\n"
            "import builtins\n"
            "import base64 as _b64\n"
            "import json as _json\n"
            "import sys as _sys\n"
            "import traceback as _tb\n"
            "_real_exec = builtins.exec\n"
            "_original_getattr = builtins.getattr\n"
            "_original_type = builtins.type\n"
        )

        # === 3. input() 오버라이드 ===
        # _sys를 사용하여 import sys 없이 동작 (safe_import에 막히지 않음)
        if preset_inputs is not None:
            parts.append(
                "# --- input() 오버라이드 ---\n"
                f"_preset_inputs = iter({preset_inputs!r})\n"
                "def input(prompt=''):\n"
                "    if prompt:\n"
                "        _sys.stdout.write(str(prompt))\n"
                "        _sys.stdout.flush()\n"
                "    try:\n"
                "        value = next(_preset_inputs)\n"
                '        _sys.stdout.write(str(value) + "\\n")\n'
                "        _sys.stdout.flush()\n"
                "        return str(value)\n"
                "    except StopIteration:\n"
                '        _sys.stdout.write("\\n")\n'
                "        _sys.stdout.flush()\n"
                '        return ""\n'
            )
        else:
            parts.append(
                "# --- input() 오버라이드 (대화형 입력 없음) ---\n"
                "def input(prompt=''):\n"
                "    if prompt:\n"
                "        _sys.stdout.write(str(prompt))\n"
                "        _sys.stdout.flush()\n"
                '    _sys.stdout.write("\\n")\n'
                "    _sys.stdout.flush()\n"
                '    return ""\n'
            )

        # === 4. 안전한 getattr 래퍼 ===
        # 샌드박스 탈출에 사용되는 위험 dunder만 선택 차단
        # type() 오버라이드는 Python import 시스템(enum.py)을 파괴하므로 하지 않는다
        parts.append(
            "# --- 안전한 getattr 래퍼 ---\n"
            "_BLOCKED_DUNDERS = {\n"
            "    '__subclasses__', '__bases__', '__mro__',\n"
            "    '__globals__', '__code__', '__func__',\n"
            "    '__builtins__', '__import__',\n"
            "}\n"
            "def _safe_getattr(obj, name, *args):\n"
            "    if isinstance(name, str) and name in _BLOCKED_DUNDERS:\n"
            '        raise AttributeError(f"접근이 제한된 속성입니다: {name}")\n'
            "    return _original_getattr(obj, name, *args)\n"
            "builtins.getattr = _safe_getattr\n"
        )

        # === 5. __import__ 차단/제한 ===
        # import depth를 추적하여 최상위 import만 검증한다.
        # depth > 0이면 허용 모듈의 내부 transitive import이므로 통과.
        if self.chapter_id >= 8:
            allowed_mods = (
                "{'math', 'random', 'string', 'copy', "
                "'collections', 'itertools', 'functools', 'datetime', "
                "'numpy', 'pandas'}"
            )
        else:
            allowed_mods = (
                "{'math', 'random', 'string', 'copy', "
                "'collections', 'itertools', 'functools', 'datetime'}"
            )

        parts.append(
            "# --- safe_import (import depth 추적) ---\n"
            f"_ALLOWED_MODULES = {allowed_mods}\n"
            "_real_import = builtins.__import__\n"
            "_import_depth = 0\n"
            "def _safe_import(name, *args, **kwargs):\n"
            "    global _import_depth\n"
            "    if _import_depth == 0:\n"
            "        top_level = name.split('.')[0]\n"
            "        if top_level not in _ALLOWED_MODULES:\n"
            "            raise ImportError(\n"
            "                f\"이 학습 환경에서는 '{name}' 모듈을 사용할 수 없습니다. \"\n"
            "                f\"허용된 모듈: {', '.join(sorted(_ALLOWED_MODULES))}\"\n"
            "            )\n"
            "    _import_depth += 1\n"
            "    try:\n"
            "        return _real_import(name, *args, **kwargs)\n"
            "    finally:\n"
            "        _import_depth -= 1\n"
            "builtins.__import__ = _safe_import\n"
        )

        # === 6. 사용자 코드 실행 ===
        # exec()에 전달할 globals에 커스텀 builtins(위험 함수 차단)를 사용한다.
        # 원본 builtins 모듈은 보존하여 import된 모듈(numpy 등)이 정상 작동하게 한다.
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

        exec_section = (
            "# --- 사용자 코드 실행 ---\n"
            f'_user_code = _b64.b64decode("{code_b64}").decode("utf-8")\n'
            "_user_ns = {}\n"
            "# 사용자 코드용 builtins: 위험 함수를 차단 래퍼로 대체\n"
            "_user_builtins = dict(builtins.__dict__)\n"
            "def _make_blocked(fn):\n"
            "    def _b(*a, **k): raise NameError(f\"'{fn}'은(는) 이 학습 환경에서 사용할 수 없습니다\")\n"
            "    return _b\n"
            "for _bname in ['exec', 'eval', 'compile', 'open', 'breakpoint', 'exit', 'quit', 'setattr', 'delattr']:\n"
            "    _user_builtins[_bname] = _make_blocked(_bname)\n"
            "_exec_globals = {'__builtins__': _user_builtins, 'input': input}\n"
        )

        # 주입 변수를 _exec_globals에 추가
        if inject_variables:
            for var_name, var_value in inject_variables.items():
                exec_section += f"_exec_globals['{var_name}'] = {var_value!r}\n"

        exec_section += (
            "try:\n"
            "    _real_exec(_user_code, _exec_globals, _user_ns)\n"
            "except Exception as _e:\n"
            "    _tb.print_exc()\n"
            "    _sys.exit(1)\n"
        )

        parts.append(exec_section)

        # === 7. 변수 추출 ===
        # 사용자 코드 실행 후 단순 타입의 변수만 JSON으로 추출
        vars_start = self._VARS_MARKER_START.strip()
        vars_end = self._VARS_MARKER_END.strip()

        parts.append(
            "# --- 변수 추출 ---\n"
            "_EXTRACTABLE_TYPES = (int, float, str, bool, list, dict, tuple, set)\n"
            "_extracted = {}\n"
            "# _exec_globals와 _user_ns 모두에서 추출 (user_ns 우선)\n"
            "_all_vars = dict(_exec_globals)\n"
            "_all_vars.update(_user_ns)\n"
            "_SYSTEM_NAMES = {'__builtins__', 'input', 'builtins'}\n"
            "\n"
            "for _name, _value in _all_vars.items():\n"
            "    if _name.startswith('_') or _name in _SYSTEM_NAMES:\n"
            "        continue\n"
            "    if _original_type(_value) == _original_type(lambda: None) or _original_type(_value) == _original_type:\n"
            "        if _original_type(_value) == _original_type:\n"
            "            _extracted[_name] = f\"<class '{_value.__name__}'>\"\n"
            "        else:\n"
            "            _extracted[_name] = f\"<function '{_name}'>\"\n"
            "        continue\n"
            "    if isinstance(_value, _EXTRACTABLE_TYPES):\n"
            "        try:\n"
            "            if isinstance(_value, set):\n"
            "                _extracted[_name] = sorted(list(_value), key=str)\n"
            "            elif isinstance(_value, tuple):\n"
            "                _extracted[_name] = list(_value)\n"
            "            else:\n"
            "                _json.dumps(_value, ensure_ascii=False)\n"
            "                _extracted[_name] = _value\n"
            "        except (TypeError, ValueError, OverflowError):\n"
            "            _extracted[_name] = str(_value)\n"
            "\n"
            f'_sys.stdout.write("{vars_start}\\n")\n'
            "_sys.stdout.write(_json.dumps(_extracted, ensure_ascii=False, default=str))\n"
            f'_sys.stdout.write("\\n{vars_end}\\n")\n'
            "_sys.stdout.flush()\n"
        )

        return "\n".join(parts)

    def _parse_result(
        self, stdout: str, stderr: str, execution_time: float
    ) -> ExecutionResult:
        """subprocess 실행 결과를 파싱한다.

        stdout에서 변수 마커를 찾아 JSON 딕셔너리를 추출하고,
        나머지를 실제 사용자 출력으로 분리한다.
        stderr가 있으면 에러 타입과 줄 번호를 파싱한다.

        Args:
            stdout: subprocess의 표준 출력
            stderr: subprocess의 표준 에러
            execution_time: 실행 시간 (초)

        Returns:
            파싱된 ExecutionResult
        """
        variables: dict = {}
        user_output = stdout

        # === 변수 추출 ===
        marker_start = self._VARS_MARKER_START.strip()
        marker_end = self._VARS_MARKER_END.strip()

        if marker_start in stdout and marker_end in stdout:
            start_idx = stdout.index(marker_start)
            end_idx = stdout.index(marker_end)

            json_str = stdout[start_idx + len(marker_start):end_idx].strip()
            user_output = stdout[:start_idx].rstrip()

            try:
                variables = json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # === 에러 파싱 ===
        error_type = None
        error_line = None
        success = True

        if stderr:
            success = False

            # 에러 타입 추출
            error_match = re.search(
                r"(\w+Error|\w+Exception):\s*(.+)",
                stderr,
                re.MULTILINE,
            )
            if error_match:
                error_type = error_match.group(1)

            # 줄 번호 추출
            line_match = re.search(
                r'File\s+"[^"]*",\s+line\s+(\d+)',
                stderr,
            )
            if line_match:
                error_line = int(line_match.group(1))

            # 서버 경로를 [코드]로 치환 (보안)
            stderr = self._sanitize_paths(stderr)

            # 에러 한국어 번역 시도
            stderr = self._translate_error(
                stderr, error_type, user_output, error_line
            )

        return ExecutionResult(
            stdout=user_output,
            stderr=stderr,
            variables=variables,
            success=success,
            error_type=error_type,
            error_line=error_line,
            execution_time=execution_time,
        )

    def _sanitize_paths(self, stderr: str) -> str:
        """에러 메시지에서 서버 파일 경로를 제거한다.

        Args:
            stderr: 원본 에러 메시지

        Returns:
            경로가 제거된 에러 메시지
        """
        sanitized = re.sub(
            r'File "([^"]*(?:tmp|temp|Temp)[^"]*)"',
            'File "[코드]"',
            stderr,
            flags=re.IGNORECASE,
        )
        sanitized = re.sub(
            r'File "(/[^"]+|[A-Z]:\\[^"]+)"',
            'File "[코드]"',
            sanitized,
        )
        sanitized = sanitized.replace(
            'File "<string>"', 'File "[사용자 코드]"'
        )
        return sanitized

    def _translate_error(
        self,
        stderr: str,
        error_type: Optional[str],
        code: str,
        error_line: Optional[int],
    ) -> str:
        """에러 메시지를 한국어로 번역한다.

        ErrorTranslator 모듈이 사용 가능하면 한국어 번역을 시도한다.

        Args:
            stderr: 원본 에러 메시지
            error_type: 에러 클래스 이름
            code: 사용자 코드
            error_line: 에러 줄 번호

        Returns:
            한국어로 번역된 에러 메시지 또는 원본 메시지
        """
        if not error_type:
            return stderr

        try:
            from core.error_translator import ErrorTranslator

            translator = ErrorTranslator()

            error_msg_match = re.search(
                rf"{re.escape(error_type)}:\s*(.+)",
                stderr,
            )
            error_msg = (
                error_msg_match.group(1).strip()
                if error_msg_match
                else stderr
            )

            translated = translator.translate(
                error_type, error_msg, code, error_line
            )
            return translated

        except ImportError:
            return stderr
