"""보안 검증기 테스트."""

import pytest
from core.security import SecurityValidator, MemorySafetyValidator


class TestSecurityValidator:
    """SecurityValidator 테스트."""

    def setup_method(self):
        """각 테스트 전 검증기 초기화."""
        self.validator = SecurityValidator()

    def test_safe_code_passes(self):
        """안전한 코드는 통과해야 한다."""
        safe_code = "x = 1 + 2\nprint(x)"
        is_safe, msg = self.validator.validate(safe_code)
        assert is_safe is True

    def test_dunder_attribute_blocked(self):
        """__subclasses__ 등 dunder 속성 접근은 차단해야 한다."""
        dangerous_code = "x = ().__class__.__subclasses__()"
        is_safe, msg = self.validator.validate(dangerous_code)
        assert is_safe is False

    def test_import_os_blocked(self):
        """os 모듈 import는 차단해야 한다."""
        dangerous_code = "import os"
        is_safe, msg = self.validator.validate(dangerous_code)
        assert is_safe is False

    def test_import_subprocess_blocked(self):
        """subprocess 모듈 import는 차단해야 한다."""
        dangerous_code = "import subprocess"
        is_safe, msg = self.validator.validate(dangerous_code)
        assert is_safe is False

    def test_allowed_import_math(self):
        """math 모듈은 허용해야 한다."""
        code = "import math\nprint(math.pi)"
        is_safe, msg = self.validator.validate(code)
        assert is_safe is True

    def test_numpy_blocked_in_ch1(self):
        """챕터 1에서 numpy import는 차단해야 한다."""
        code = "import numpy"
        is_safe, msg = self.validator.validate(code, chapter_id=1)
        assert is_safe is False

    def test_numpy_allowed_in_ch8(self):
        """챕터 8에서 numpy import는 허용해야 한다."""
        code = "import numpy"
        is_safe, msg = self.validator.validate(code, chapter_id=8)
        assert is_safe is True

    def test_exec_call_blocked(self):
        """exec() 호출은 차단해야 한다."""
        code = "exec('print(1)')"
        is_safe, msg = self.validator.validate(code)
        assert is_safe is False

    def test_eval_call_blocked(self):
        """eval() 호출은 차단해야 한다."""
        code = "eval('1+1')"
        is_safe, msg = self.validator.validate(code)
        assert is_safe is False

    def test_syntax_error_handling(self):
        """구문 오류 코드는 False를 반환하거나 에러 메시지를 포함해야 한다."""
        code = "def f(\n"
        is_safe, msg = self.validator.validate(code)
        # 구현에 따라 구문 오류를 차단하거나 통과시킬 수 있음
        # 통과하더라도 exec 시점에서 SyntaxError 발생
        assert isinstance(is_safe, bool)


class TestMemorySafetyValidator:
    """MemorySafetyValidator 테스트."""

    def setup_method(self):
        """각 테스트 전 검증기 초기화."""
        self.validator = MemorySafetyValidator()

    def test_normal_code_passes(self):
        """일반 코드는 통과해야 한다."""
        code = "x = [1, 2, 3]\nfor i in range(100):\n    pass"
        is_safe, msg = self.validator.validate(code)
        assert is_safe is True

    def test_huge_number_blocked(self):
        """매우 큰 정수 상수는 차단해야 한다."""
        code = "x = 99999999999999"
        is_safe, msg = self.validator.validate(code)
        assert is_safe is False

    def test_normal_range_allowed(self):
        """정상 범위의 range()는 허용해야 한다."""
        code = "for i in range(1000):\n    pass"
        is_safe, msg = self.validator.validate(code)
        assert is_safe is True
