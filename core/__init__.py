"""메타코드 파이썬 학습 플랫폼 - 코어 모듈.

코드 실행, 채점, 진행도 관리, 힌트, 에러 번역 등
핵심 비즈니스 로직을 담당한다.

모듈 구성:
    security: AST 기반 보안 검증 (SecurityValidator, MemorySafetyValidator)
    executor: subprocess 기반 코드 실행 (CodeExecutor, VirtualFileSystem)
    error_translator: 에러 한국어 번역 (ErrorTranslator)
    utils: 공통 유틸리티 (JSON 로드, 출력 정규화 등)
"""

from core.security import MemorySafetyValidator, SecurityValidator
from core.executor import CodeExecutor, ExecutionResult, VirtualFileSystem
from core.error_translator import ErrorTranslator
from core.utils import (
    get_data_dir,
    load_chapter_data,
    load_json,
    load_problems,
    load_quiz,
    normalize_output,
    truncate_output,
)

__all__ = [
    # security
    "SecurityValidator",
    "MemorySafetyValidator",
    # executor
    "CodeExecutor",
    "ExecutionResult",
    "VirtualFileSystem",
    # error_translator
    "ErrorTranslator",
    # utils
    "get_data_dir",
    "load_json",
    "load_chapter_data",
    "load_problems",
    "load_quiz",
    "normalize_output",
    "truncate_output",
]
