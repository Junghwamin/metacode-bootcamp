"""Python 에러 메시지를 초보자 친화적 한국어로 번역하는 모듈.

Python 에러 메시지는 영어이고 기술 용어가 많아
프로그래밍 초보자에게는 이해하기 어렵다.
이 모듈은 주요 에러 유형을 한국어로 번역하고,
자주 하는 실수 패턴을 감지하여 구체적인 해결 방법을 제안한다.

번역 대상 에러 (10종):
    SyntaxError, NameError, TypeError, IndexError, KeyError,
    ValueError, IndentationError, ZeroDivisionError,
    AttributeError, FileNotFoundError
"""

import re
from typing import Optional


class ErrorTranslator:
    """Python 에러 메시지를 초보자 친화적 한국어로 번역하는 클래스.

    번역 결과는 마크다운 형식으로 반환되며,
    에러 유형, 원인 설명, 흔한 실수 패턴, 원본 메시지를 포함한다.

    Attributes:
        ERROR_TRANSLATIONS: 에러 유형별 한국어 번역 정보 딕셔너리
    """

    # === 에러 유형별 한국어 번역 ===
    # 각 항목 구조: {title: 제목, description: 설명, common_causes: [흔한 원인들]}
    ERROR_TRANSLATIONS: dict = {
        "SyntaxError": {
            "title": "문법 오류",
            "description": (
                "파이썬이 코드를 읽다가 이해할 수 없는 부분을 발견했습니다. "
                "괄호, 따옴표, 콜론 등이 빠졌거나 잘못 사용된 경우가 많습니다."
            ),
            "common_causes": [
                "괄호 `()`, `[]`, `{}`의 짝이 맞지 않음",
                "문자열의 따옴표가 닫히지 않음 (`'hello` → `'hello'`)",
                "if, for, while, def 뒤에 콜론(`:`)이 빠짐",
                "등호(`=`)와 비교(`==`)를 혼동함",
                '한글 괄호나 따옴표를 사용함 (（）→ (), "\u201c\u201d" → "")',
            ],
        },
        "NameError": {
            "title": "이름 오류",
            "description": (
                "정의되지 않은 변수나 함수를 사용하려고 했습니다. "
                "오타가 있거나, 변수를 아직 만들지 않았을 수 있습니다."
            ),
            "common_causes": [
                "변수 이름에 오타가 있음 (예: `pritn` → `print`)",
                "변수를 사용하기 전에 먼저 값을 할당하지 않음",
                "대소문자가 다름 (파이썬은 `name`과 `Name`을 다르게 인식)",
                "문자열에 따옴표를 빼먹음 (예: `hello` → `'hello'`)",
            ],
        },
        "TypeError": {
            "title": "타입 오류",
            "description": (
                "서로 다른 종류의 데이터를 잘못된 방식으로 함께 사용했습니다. "
                "예를 들어, 숫자와 문자열을 더하거나, 함수 호출 방법이 잘못된 경우입니다."
            ),
            "common_causes": [
                "숫자와 문자열을 `+`로 합치려 함 (예: `1 + '2'` → `1 + int('2')`)",
                "함수에 필요한 인자를 빼먹거나 너무 많이 넣음",
                "호출할 수 없는 것을 호출함 (예: `x = 5; x()` → 변수에 괄호 사용)",
                "`None`에 대해 연산을 수행함 (함수가 return 없이 끝난 경우)",
            ],
        },
        "IndexError": {
            "title": "인덱스 오류",
            "description": (
                "리스트나 문자열에서 존재하지 않는 위치를 참조했습니다. "
                "인덱스가 범위를 벗어났습니다."
            ),
            "common_causes": [
                "리스트 길이보다 큰 인덱스를 사용함 (길이 3인 리스트의 `[3]` 접근)",
                "파이썬 인덱스는 0부터 시작함 (첫 번째 요소는 `[0]`)",
                "빈 리스트 `[]`에서 요소를 꺼내려 함",
                "반복문에서 리스트를 수정하면서 동시에 접근함",
            ],
        },
        "KeyError": {
            "title": "키 오류",
            "description": (
                "딕셔너리에 존재하지 않는 키로 접근했습니다. "
                "키 이름을 확인하거나 `.get()` 메서드를 사용해 보세요."
            ),
            "common_causes": [
                "딕셔너리 키 이름에 오타가 있음",
                "대소문자가 다름 (예: `'Name'`과 `'name'`은 다른 키)",
                "존재 여부를 먼저 확인하지 않음 (`if key in dict:` 사용)",
                "`.get(key, 기본값)` 메서드를 사용하면 안전하게 접근 가능",
            ],
        },
        "ValueError": {
            "title": "값 오류",
            "description": (
                "함수에 올바른 타입이지만 잘못된 값이 전달되었습니다. "
                "예를 들어, 숫자가 아닌 문자열을 정수로 변환하려 한 경우입니다."
            ),
            "common_causes": [
                "`int('abc')`: 숫자가 아닌 문자열을 정수로 변환 시도",
                "`int('3.14')`: 소수점이 있는 문자열은 `float()`로 먼저 변환해야 함",
                "`list.remove(값)`: 리스트에 없는 값을 제거하려 함",
                "`input()`으로 받은 값을 변환 전에 검증하지 않음",
            ],
        },
        "IndentationError": {
            "title": "들여쓰기 오류",
            "description": (
                "코드의 들여쓰기(공백/탭)가 잘못되었습니다. "
                "파이썬에서는 들여쓰기가 코드 블록을 구분하는 중요한 문법입니다."
            ),
            "common_causes": [
                "if, for, while, def, class 다음 줄에 들여쓰기가 없음",
                "같은 블록 안에서 들여쓰기 수준이 다름 (스페이스 2개 vs 4개 혼용)",
                "탭(Tab)과 스페이스(Space)를 섞어 사용함",
                "불필요한 들여쓰기가 있음 (if 없이 갑자기 들여쓰기)",
            ],
        },
        "ZeroDivisionError": {
            "title": "0으로 나누기 오류",
            "description": (
                "숫자를 0으로 나누려고 했습니다. "
                "수학에서와 마찬가지로 0으로 나누기는 정의되지 않습니다."
            ),
            "common_causes": [
                "나눗셈 전에 분모가 0인지 확인하지 않음",
                "변수가 0이 될 수 있는 경우를 고려하지 않음",
                "`if divisor != 0:` 조건으로 먼저 검사하세요",
                "`%` (나머지) 연산에서도 0으로 나누면 같은 오류 발생",
            ],
        },
        "AttributeError": {
            "title": "속성 오류",
            "description": (
                "객체에 존재하지 않는 속성이나 메서드를 사용하려 했습니다. "
                "오타이거나, 해당 타입에서 지원하지 않는 기능일 수 있습니다."
            ),
            "common_causes": [
                "메서드 이름에 오타가 있음 (예: `list.apend()` → `list.append()`)",
                "다른 타입의 메서드를 사용함 (예: 정수에 `.split()` 사용)",
                "`None` 객체의 메서드를 호출함 (함수 반환값이 None인 경우)",
                "`type()` 함수로 객체의 타입을 먼저 확인해 보세요",
            ],
        },
        "FileNotFoundError": {
            "title": "파일 없음 오류",
            "description": (
                "열려는 파일을 찾을 수 없습니다. "
                "이 학습 환경에서는 가상 파일시스템을 사용합니다."
            ),
            "common_causes": [
                "파일 이름에 오타가 있음",
                "파일 확장자가 빠짐 (예: `data` → `data.txt`)",
                "이 학습 환경에서는 실제 파일 대신 가상 파일을 사용합니다",
                "문제에서 제공된 파일 이름을 정확히 사용했는지 확인하세요",
            ],
        },
    }

    # === 전각 문자 → 반각 문자 매핑 ===
    # 한국어 키보드에서 자주 발생하는 전각 문자 실수
    FULLWIDTH_MAP: dict = {
        "：": ":",
        "＝": "=",
        "（": "(",
        "）": ")",
        "［": "[",
        "］": "]",
        "｛": "{",
        "｝": "}",
        "\u201c": '"',   # 왼쪽 큰따옴표 "
        "\u201d": '"',   # 오른쪽 큰따옴표 "
        "\u2018": "'",   # 왼쪽 작은따옴표 '
        "\u2019": "'",   # 오른쪽 작은따옴표 '
        "；": ";",
        "，": ",",
        "＋": "+",
        "－": "-",
        "＊": "*",
        "／": "/",
    }

    def translate(
        self,
        error_type: str,
        error_msg: str,
        code: str = "",
        line_no: Optional[int] = None,
    ) -> str:
        """에러를 초보자 친화적 한국어 마크다운으로 번역한다.

        Args:
            error_type: 에러 클래스 이름 (예: "SyntaxError", "NameError")
            error_msg: 에러 메시지 원문 (영어)
            code: 에러가 발생한 전체 소스코드 (선택, 실수 패턴 감지에 사용)
            line_no: 에러 발생 줄 번호 (선택)

        Returns:
            마크다운 형식의 한국어 에러 설명 문자열

        Examples:
            >>> translator = ErrorTranslator()
            >>> result = translator.translate("NameError", "name 'x' is not defined")
            >>> "이름 오류" in result
            True
        """
        # 번역 정보 조회 (알 수 없는 에러는 기본 메시지 사용)
        info = self.ERROR_TRANSLATIONS.get(error_type, {
            "title": "오류",
            "description": "코드 실행 중 오류가 발생했습니다.",
            "common_causes": ["에러 메시지를 자세히 읽어보세요."],
        })

        # === 마크다운 조립 ===
        lines: list[str] = []

        lines.append("**코드에서 오류가 발생했어요**")
        lines.append("")
        lines.append("걱정 마세요! 오류는 프로그래머에게 흔한 일입니다.")
        lines.append("")

        # 에러 제목과 설명
        lines.append(f"### {info['title']} ({error_type})")
        lines.append(info["description"])
        lines.append("")

        # 줄 번호 정보
        if line_no is not None:
            lines.append(f"**{line_no}번째 줄** 근처에서 발생했습니다.")
            lines.append("")

        # 흔한 실수 패턴 감지
        if code:
            mistake_hint = self._detect_common_mistakes(code, error_type)
            if mistake_hint:
                lines.append(f"**감지된 실수:** {mistake_hint}")
                lines.append("")

        # 자주 하는 실수 목록
        lines.append("**자주 하는 실수:**")
        for cause in info["common_causes"]:
            lines.append(f"- {cause}")
        lines.append("")

        # 원본 메시지
        lines.append(f"**원본 메시지:** `{error_msg}`")

        return "\n".join(lines)

    def _detect_common_mistakes(
        self, code: str, error_type: str
    ) -> Optional[str]:
        """코드에서 초보자가 자주 하는 실수 패턴을 감지한다.

        휴리스틱 기반으로 코드를 분석하여 흔한 실수를 찾아낸다.
        감지 대상: 전각 문자, 대소문자 오류, 한글 따옴표/괄호, 탭/스페이스 혼용

        Args:
            code: 에러가 발생한 소스코드
            error_type: 에러 타입 이름 (감지 로직 분기에 사용)

        Returns:
            감지된 실수에 대한 설명 문자열, 감지 안 되면 None
        """
        # --- 전각 문자 감지 ---
        # 한국어 입력 상태에서 코딩하면 전각 문자가 들어가기 쉽다
        for fullwidth, halfwidth in self.FULLWIDTH_MAP.items():
            if fullwidth in code:
                return (
                    f"전각 문자 `{fullwidth}`가 발견되었습니다. "
                    f"반각 문자 `{halfwidth}`로 바꿔주세요. "
                    f"(한글 입력 상태에서 특수문자를 입력하면 전각 문자가 됩니다)"
                )

        # --- Print 대소문자 오류 ---
        # 다른 언어에서 넘어온 학습자가 자주 하는 실수
        if re.search(r'\bPrint\s*\(', code):
            return (
                "`Print`가 발견되었습니다. "
                "파이썬에서는 소문자 `print`를 사용해야 합니다."
            )

        # --- 한글 괄호/따옴표 ---
        korean_brackets = {"（": "(", "）": ")", "「": "[", "」": "]"}
        for k_bracket, correct in korean_brackets.items():
            if k_bracket in code:
                return (
                    f"한글 괄호 `{k_bracket}`가 발견되었습니다. "
                    f"영문 괄호 `{correct}`로 바꿔주세요."
                )

        # --- 탭/스페이스 혼용 ---
        if error_type == "IndentationError":
            has_tab = "\t" in code
            has_spaces = bool(re.search(r'^    ', code, re.MULTILINE))
            if has_tab and has_spaces:
                return (
                    "탭(Tab)과 스페이스(Space)가 섞여 있습니다. "
                    "하나로 통일해 주세요. 스페이스 4칸을 권장합니다."
                )

        return None

    def sanitize_traceback(self, stderr: str) -> str:
        """traceback에서 서버 내부 경로를 제거한다.

        보안상 서버 파일 경로가 사용자에게 노출되면 안 되므로,
        실행 환경 관련 경로를 `[서버경로]`로 치환한다.
        사용자 코드 관련 프레임(<string>, <user_code>)만 남긴다.

        Args:
            stderr: subprocess에서 캡처한 에러 출력 문자열

        Returns:
            서버 경로가 제거된 안전한 traceback 문자열
        """
        if not stderr:
            return ""

        # Step 1: 서버 경로 패턴 치환
        # /home/user/..., /app/..., /tmp/... 등 서버 경로를 마스킹
        sanitized = re.sub(
            r'File "(/home/|/app/|/tmp/|/var/|C:\\|/usr/)[^"]*"',
            'File "[코드]"',
            stderr,
        )

        # Step 2: 임시 파일 경로 치환
        # subprocess 실행 시 생성되는 임시 파일 경로
        sanitized = re.sub(
            r'File "[^"]*(?:tmp|temp)[^"]*\.py"',
            'File "[코드]"',
            sanitized,
            flags=re.IGNORECASE,
        )

        # Step 3: 사용자 코드 프레임 표시 정리
        sanitized = sanitized.replace(
            'File "<string>"', 'File "[사용자 코드]"'
        )
        sanitized = sanitized.replace(
            'File "<user_code>"', 'File "[사용자 코드]"'
        )

        return sanitized
