"""AST 기반 보안 검증 모듈.

사용자 코드를 실행하기 전에 AST를 분석하여
위험한 패턴(dunder 속성 접근, 위험 모듈 import 등)을 사전 차단한다.

보안 전략:
    1단계 - AST 정적 분석: SecurityValidator가 코드 구조를 검사
    2단계 - 메모리 안전성: MemorySafetyValidator가 리소스 남용을 검사
    3단계 - 런타임 샌드박스: executor.py에서 builtins 래핑으로 동적 차단

Note:
    AST 분석만으로는 모든 공격을 차단할 수 없으므로,
    executor.py의 런타임 샌드박스와 반드시 병행해야 한다.
    예: getattr(obj, '__' + 'subclasses__')() 같은 문자열 결합 우회
"""

import ast
from typing import Tuple


class SecurityValidator(ast.NodeVisitor):
    """AST 기반 보안 검증기.

    사용자 코드의 AST를 순회하며 위험한 패턴을 탐지한다.
    차단 대상:
        - dunder 속성 접근 (__subclasses__, __globals__ 등)
        - 위험 모듈 import (os, sys, subprocess 등)
        - 챕터별 허용되지 않는 모듈 사용

    Attributes:
        BLOCKED_ATTRIBUTES: 절대 접근 불가한 dunder 속성 목록
        ALLOWED_DUNDERS: 학습용으로 허용하는 dunder 속성 목록
        ALWAYS_ALLOWED_MODULES: 모든 챕터에서 허용하는 표준 라이브러리 모듈
        CH8_EXTRA_MODULES: 챕터 8(데이터 분석)에서 추가 허용하는 모듈
        ALWAYS_BLOCKED_MODULES: 어떤 챕터에서도 절대 차단하는 위험 모듈
    """

    # === 차단할 dunder 속성 목록 ===
    # 이 속성들은 Python 내부 구조 접근을 통한 샌드박스 탈출에 사용될 수 있다.
    # 예: ().__class__.__bases__[0].__subclasses__() → 모든 클래스 열거 가능
    BLOCKED_ATTRIBUTES: set = {
        "__subclasses__",  # 클래스 계층 탐색 → 임의 클래스 인스턴스화
        "__bases__",       # 상위 클래스 접근 → object까지 도달 가능
        "__mro__",         # Method Resolution Order → 클래스 계층 전체 노출
        "__globals__",     # 함수의 전역 네임스페이스 접근 → 모듈 탈취
        "__code__",        # 함수 바이트코드 접근/수정 → 임의 코드 실행
        "__func__",        # 바운드 메서드의 원본 함수 접근
        "__builtins__",    # 내장 함수 딕셔너리 접근 → __import__ 탈취
        "__import__",      # import 시스템 직접 호출
        "__dict__",        # 객체 속성 딕셔너리 직접 접근
        "__class__",       # 인스턴스에서 클래스 객체 접근 → 계층 탐색 시작점
    }

    # === 학습 목적으로 허용하는 dunder 속성 ===
    # 파이썬 기초 학습에서 자주 사용하는 매직 메서드
    ALLOWED_DUNDERS: set = {
        "__init__",   # 생성자: 클래스 기초 학습 필수
        "__str__",    # 문자열 표현: print() 동작 이해
        "__repr__",   # 개발자 표현: 디버깅 학습
        "__len__",    # 길이 프로토콜: len() 커스터마이징
        "__name__",   # 모듈/클래스 이름: 메타정보 접근
    }

    # === 챕터별 모듈 허용 정책 ===
    # 기본 허용: 안전한 순수 계산/유틸 모듈만 포함
    ALWAYS_ALLOWED_MODULES: set = {
        "math",         # 수학 함수 (sin, cos, sqrt 등)
        "random",       # 난수 생성 (파일시스템 접근 없음)
        "string",       # 문자열 상수 (ascii_letters 등)
        "copy",         # 깊은/얕은 복사
        "collections",  # namedtuple, Counter, deque 등
        "itertools",    # 반복자 조합 도구
        "functools",    # 고차 함수 도구 (reduce 등)
        "datetime",     # 날짜/시간 처리
    }

    # 챕터 8(데이터 분석) 전용 추가 허용 모듈
    CH8_EXTRA_MODULES: set = {
        "numpy",   # 수치 계산 라이브러리
        "pandas",  # 데이터 분석 라이브러리
    }

    # === 절대 차단 모듈 ===
    # 파일시스템, 네트워크, 프로세스 접근 등 위험한 모듈
    ALWAYS_BLOCKED_MODULES: set = {
        "os",           # 파일시스템, 환경변수, 프로세스 관리
        "sys",          # 인터프리터 내부 접근
        "subprocess",   # 외부 프로세스 실행
        "shutil",       # 파일/디렉토리 고수준 조작
        "pathlib",      # 파일 경로 조작
        "socket",       # 네트워크 소켓
        "http",         # HTTP 서버/클라이언트
        "urllib",       # URL 처리/네트워크 요청
        "requests",     # HTTP 요청 라이브러리
        "importlib",    # import 시스템 직접 접근
        "ctypes",       # C 라이브러리 호출 → 메모리 접근
        "signal",       # 프로세스 시그널 제어
        "pickle",       # 객체 직렬화 → 임의 코드 실행 가능
        "shelve",       # pickle 기반 영속 저장소
        "sqlite3",      # 데이터베이스 접근
        "__builtins__",  # 내장 함수 딕셔너리
    }

    def __init__(self) -> None:
        """SecurityValidator 초기화.

        violations 리스트를 비워 새로운 검증 세션을 시작한다.
        """
        self.violations: list[str] = []
        self._chapter_id: int = 1

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """속성 접근 노드(obj.attr)를 검사한다.

        dunder 속성(__로 시작하고 끝나는 이름) 중
        ALLOWED_DUNDERS에 포함되지 않은 것은 차단한다.

        Args:
            node: AST Attribute 노드 (예: obj.__globals__)
        """
        attr_name = node.attr

        # dunder 패턴 검사: __xxx__ 형태
        if (
            attr_name.startswith("__")
            and attr_name.endswith("__")
            and attr_name not in self.ALLOWED_DUNDERS
        ):
            self.violations.append(
                f"'{attr_name}' 속성에 접근할 수 없습니다. "
                f"이 속성은 보안상 제한됩니다."
            )

        # 자식 노드 계속 방문
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """이름 참조 노드를 검사한다.

        dunder 이름을 변수처럼 직접 참조하는 것을 차단한다.
        예: __import__('os') 같은 직접 호출

        Args:
            node: AST Name 노드 (예: __import__)
        """
        name = node.id

        if (
            name.startswith("__")
            and name.endswith("__")
            and name not in self.ALLOWED_DUNDERS
        ):
            self.violations.append(
                f"'{name}'을(를) 직접 사용할 수 없습니다. "
                f"이 이름은 보안상 제한됩니다."
            )

        self.generic_visit(node)

    # === 차단할 내장 함수 이름 ===
    # AST 단계에서 위험한 내장 함수 호출을 사전 차단한다.
    # 런타임 builtins 오버라이드는 import 시스템을 파괴할 수 있으므로,
    # 정적 분석에서 최대한 잡아내는 것이 안전하다.
    BLOCKED_FUNCTIONS: set = {
        "exec",         # 동적 코드 실행
        "eval",         # 동적 표현식 평가
        "compile",      # 코드 컴파일
        "open",         # 파일시스템 접근
        "breakpoint",   # 디버거 진입
        "globals",      # 전역 네임스페이스 접근
        "locals",       # 지역 네임스페이스 접근
        "vars",         # 객체 속성 딕셔너리 접근
        "exit",         # 프로세스 종료
        "quit",         # 프로세스 종료
        "setattr",      # 속성 동적 변경
        "delattr",      # 속성 동적 삭제
    }

    def visit_Call(self, node: ast.Call) -> None:
        """함수 호출 노드를 검사한다.

        위험한 내장 함수(exec, eval, open 등)의 직접 호출을 차단한다.
        단, 챕터 6(파일 입출력)에서는 open()을 VirtualFileSystem으로 대체하므로
        AST 단계에서 차단하지 않는다.

        Args:
            node: AST Call 노드
        """
        # 이름으로 직접 호출: exec("..."), open("file")
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            # 챕터 6에서는 open()을 VFS로 대체하므로 AST 차단에서 제외
            if func_name == "open" and self._chapter_id == 6:
                pass
            elif func_name in self.BLOCKED_FUNCTIONS:
                self.violations.append(
                    f"'{func_name}()' 함수는 이 학습 환경에서 사용할 수 없습니다."
                )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """import 문을 검사한다.

        챕터별 허용 모듈 정책에 따라 검증한다.
        항상 차단 모듈은 어떤 챕터에서도 import 불가하고,
        허용 목록에 없는 모듈도 차단한다.

        Args:
            node: AST Import 노드 (예: import os)
        """
        for alias in node.names:
            self._check_module(alias.name, node.lineno)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """from ... import 문을 검사한다.

        모듈의 최상위 패키지 이름을 기준으로 검증한다.
        예: from os.path import join → 'os'가 차단 대상이므로 차단

        Args:
            node: AST ImportFrom 노드 (예: from os import path)
        """
        if node.module:
            # 최상위 패키지 이름 추출 (예: os.path → os)
            top_level = node.module.split(".")[0]
            self._check_module(top_level, node.lineno)

        self.generic_visit(node)

    def _check_module(self, module_name: str, lineno: int) -> None:
        """모듈 이름이 현재 챕터에서 허용되는지 검사한다.

        검증 순서:
            1. 항상 차단 모듈이면 즉시 차단
            2. 항상 허용 모듈이면 통과
            3. Ch8 추가 허용 모듈이면 챕터 확인 후 판단
            4. 그 외 알 수 없는 모듈은 차단

        Args:
            module_name: import할 모듈의 최상위 패키지 이름
            lineno: 해당 import 문의 소스코드 줄 번호
        """
        # 최상위 패키지 이름 추출
        top_level = module_name.split(".")[0]

        # Step 1: 항상 차단 목록 검사
        if top_level in self.ALWAYS_BLOCKED_MODULES:
            self.violations.append(
                f"'{module_name}' 모듈은 보안상 사용할 수 없습니다. "
                f"(줄 {lineno})"
            )
            return

        # Step 2: 항상 허용 목록 검사
        if top_level in self.ALWAYS_ALLOWED_MODULES:
            return

        # Step 3: Ch8 추가 허용 모듈 검사
        if top_level in self.CH8_EXTRA_MODULES:
            if self._chapter_id >= 8:
                return
            else:
                self.violations.append(
                    f"'{module_name}' 모듈은 챕터 8부터 사용할 수 있습니다. "
                    f"(줄 {lineno})"
                )
                return

        # Step 4: 허용 목록에 없는 모듈은 차단
        self.violations.append(
            f"'{module_name}' 모듈은 이 학습 환경에서 사용할 수 없습니다. "
            f"(줄 {lineno})"
        )

    def validate(self, code: str, chapter_id: int = 1) -> Tuple[bool, str]:
        """사용자 코드의 보안을 검증한다.

        AST 파싱 → 노드 방문(위험 패턴 탐지) → 결과 반환의 파이프라인을 수행한다.

        Args:
            code: 검증할 Python 소스코드 문자열
            chapter_id: 현재 학습 챕터 번호 (1~8, 모듈 허용 범위 결정)

        Returns:
            (is_safe, message) 튜플:
                - is_safe=True: 안전한 코드, message는 빈 문자열
                - is_safe=False: 위험 발견, message는 "보안 오류: {상세 내용}"

        Examples:
            >>> validator = SecurityValidator()
            >>> validator.validate("print('hello')")
            (True, '')
            >>> validator.validate("import os")
            (False, "보안 오류: 'os' 모듈은 보안상 사용할 수 없습니다. (줄 1)")
        """
        # 검증 상태 초기화
        self.violations = []
        self._chapter_id = chapter_id

        # Step 1: AST 파싱
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # 구문 오류는 보안 문제가 아니므로 통과시킨다.
            # 실행 단계에서 자연스러운 SyntaxError로 처리된다.
            return (True, "")

        # Step 2: AST 노드 방문 (위험 패턴 탐지)
        self.visit(tree)

        # Step 3: 결과 반환
        if self.violations:
            # 발견된 모든 위반 사항을 줄바꿈으로 연결
            message = "보안 오류: " + "; ".join(self.violations)
            return (False, message)

        return (True, "")


class MemorySafetyValidator(ast.NodeVisitor):
    """메모리 안전성 검증기.

    사용자 코드가 과도한 메모리나 CPU를 소모하는 패턴을 사전 차단한다.
    subprocess 타임아웃은 최후의 방어선이므로,
    정적 분석 단계에서 명백한 리소스 남용을 미리 잡아내는 것이 효율적이다.

    차단 대상:
        - 10^6을 초과하는 거대 정수 상수 (메모리 폭발)
        - range(10**7) 같은 거대 반복 (CPU/메모리 과다 사용)
        - "x" * 10**8 같은 문자열 곱셈 (메모리 폭발)

    Note:
        이 검증은 상수 표현식만 감지할 수 있다.
        변수를 사용한 간접적 리소스 남용(n=10**8; range(n))은
        subprocess 타임아웃에 의존한다.
    """

    # 리소스 제한 임계값 (10^6 = 1,000,000)
    # 이 값을 초과하는 상수는 학습 목적으로 부적절하다고 판단
    MAX_CONSTANT_VALUE: int = 10 ** 6

    def __init__(self) -> None:
        """MemorySafetyValidator 초기화."""
        self.violations: list[str] = []

    def visit_Constant(self, node: ast.Constant) -> None:
        """상수 노드를 검사한다.

        정수 상수가 MAX_CONSTANT_VALUE를 초과하면 차단한다.
        문자열이나 실수 상수는 검사하지 않는다.

        Args:
            node: AST Constant 노드
        """
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            if abs(node.value) > self.MAX_CONSTANT_VALUE:
                self.violations.append(
                    f"너무 큰 숫자({node.value:,})가 사용되었습니다. "
                    f"학습 환경에서는 {self.MAX_CONSTANT_VALUE:,} 이하의 숫자를 사용해 주세요."
                )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """함수 호출 노드를 검사한다.

        range() 호출의 인자가 상수이고 MAX_CONSTANT_VALUE를 초과하면 차단한다.
        range(start, stop)이나 range(stop) 형태를 모두 감지한다.

        Args:
            node: AST Call 노드
        """
        # range() 호출 감지
        if isinstance(node.func, ast.Name) and node.func.id == "range":
            # range()의 마지막 위치 인자를 검사 (stop 값)
            # range(stop) → args[0], range(start, stop) → args[1]
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, int):
                    if abs(arg.value) > self.MAX_CONSTANT_VALUE:
                        self.violations.append(
                            f"range()에 너무 큰 값({arg.value:,})이 사용되었습니다. "
                            f"학습 환경에서는 {self.MAX_CONSTANT_VALUE:,} 이하로 제한됩니다."
                        )

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """이항 연산 노드를 검사한다.

        곱셈(*) 연산에서 한쪽이 상수이고 MAX_CONSTANT_VALUE를 초과하면 차단한다.
        주로 "x" * 10**8 같은 문자열/리스트 곱셈을 방지한다.

        Args:
            node: AST BinOp 노드
        """
        if isinstance(node.op, ast.Mult):
            # 좌항 또는 우항이 거대 상수인지 검사
            for operand in (node.left, node.right):
                if isinstance(operand, ast.Constant) and isinstance(operand.value, int):
                    if abs(operand.value) > self.MAX_CONSTANT_VALUE:
                        self.violations.append(
                            f"곱셈에 너무 큰 값({operand.value:,})이 사용되었습니다. "
                            f"메모리 부족이 발생할 수 있어 제한됩니다."
                        )

        self.generic_visit(node)

    def validate(self, code: str) -> Tuple[bool, str]:
        """사용자 코드의 메모리 안전성을 검증한다.

        AST 파싱 → 노드 방문(리소스 남용 탐지) → 결과 반환.

        Args:
            code: 검증할 Python 소스코드 문자열

        Returns:
            (is_safe, message) 튜플:
                - is_safe=True: 안전한 코드, message는 빈 문자열
                - is_safe=False: 위험 발견, message는 "보안 오류: {상세 내용}"
        """
        self.violations = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            # 구문 오류는 메모리 안전성 문제가 아님
            return (True, "")

        self.visit(tree)

        if self.violations:
            message = "보안 오류: " + "; ".join(self.violations)
            return (False, message)

        return (True, "")
