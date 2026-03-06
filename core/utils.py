"""공통 유틸리티 함수 모음.

JSON 데이터 로드, 출력 정규화, 데이터 경로 관리 등
여러 모듈에서 공통으로 사용하는 유틸리티 함수를 제공한다.
"""

import json
from pathlib import Path
from typing import Any, Optional


# 데이터 디렉토리 경로
_BASE_DIR = Path(__file__).parent.parent
_DATA_DIR = _BASE_DIR / "data"


def get_data_dir() -> Path:
    """데이터 디렉토리 경로를 반환한다.

    Returns:
        Path: data 디렉토리 절대 경로
    """
    return _DATA_DIR


def load_json(path: Path) -> Optional[Any]:
    """JSON 파일을 로드한다.

    파일이 없거나 파싱 실패 시 None을 반환한다.

    Args:
        path: JSON 파일의 Path 객체

    Returns:
        Any | None: 파싱된 데이터 또는 None
    """
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        return None


def load_chapter_data(chapter_id: int) -> Optional[dict]:
    """챕터 데이터 JSON을 로드한다.

    Args:
        chapter_id: 챕터 번호 (1~8)

    Returns:
        dict | None: 챕터 데이터 또는 None
    """
    path = _DATA_DIR / "chapters" / f"chapter{chapter_id}.json"
    return load_json(path)


def load_problems(chapter_id: int) -> Optional[dict]:
    """챕터 문제 JSON을 로드한다.

    Args:
        chapter_id: 챕터 번호 (1~8)

    Returns:
        dict | None: 문제 데이터 또는 None
    """
    path = _DATA_DIR / "problems" / f"chapter{chapter_id}_problems.json"
    return load_json(path)


def load_quiz(chapter_id: int) -> Optional[dict]:
    """챕터 퀴즈 JSON을 로드한다.

    Args:
        chapter_id: 챕터 번호 (1~8)

    Returns:
        dict | None: 퀴즈 데이터 또는 None
    """
    path = _DATA_DIR / "quizzes" / f"chapter{chapter_id}_quiz.json"
    return load_json(path)


def normalize_output(text: str) -> str:
    """출력 문자열을 정규화한다.

    각 줄의 앞뒤 공백을 제거하고 빈 줄을 없앤다.
    채점 비교 시 공백 차이로 인한 오답을 방지한다.

    Args:
        text: 정규화할 출력 문자열

    Returns:
        str: 정규화된 문자열
    """
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    return "\n".join(non_empty).strip()


def truncate_output(text: str, max_lines: int = 50, max_chars: int = 2000) -> str:
    """출력을 적절한 길이로 잘라낸다.

    너무 긴 출력은 UI에서 가독성이 떨어지므로 줄 수와 문자 수로 제한한다.

    Args:
        text: 자를 출력 문자열
        max_lines: 최대 줄 수 (기본 50)
        max_chars: 최대 문자 수 (기본 2000)

    Returns:
        str: 잘린 출력 (잘린 경우 끝에 안내 메시지 추가)
    """
    if not text:
        return ""

    lines = text.splitlines()
    truncated = False

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True

    result = "\n".join(lines)

    if len(result) > max_chars:
        result = result[:max_chars]
        truncated = True

    if truncated:
        result += "\n... (출력이 너무 길어 잘렸습니다)"

    return result
