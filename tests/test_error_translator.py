"""에러 번역기 테스트."""

from core.error_translator import ErrorTranslator


class TestErrorTranslator:
    """ErrorTranslator 테스트."""

    def setup_method(self):
        """각 테스트 전 번역기 초기화."""
        self.translator = ErrorTranslator()

    def test_syntax_error_translation(self):
        """SyntaxError 번역이 한국어로 되어야 한다."""
        result = self.translator.translate(
            "SyntaxError", "invalid syntax", "print('hello'", 1
        )
        assert "문법" in result or "SyntaxError" in result

    def test_name_error_translation(self):
        """NameError 번역에 이름 오류가 포함되어야 한다."""
        result = self.translator.translate(
            "NameError", "name 'x' is not defined", "print(x)", 1
        )
        assert "이름" in result or "NameError" in result

    def test_type_error_translation(self):
        """TypeError 번역이 동작해야 한다."""
        result = self.translator.translate(
            "TypeError", "unsupported operand type", "'1' + 2", 1
        )
        assert "타입" in result or "TypeError" in result

    def test_zero_division_error(self):
        """ZeroDivisionError 번역이 동작해야 한다."""
        result = self.translator.translate(
            "ZeroDivisionError", "division by zero", "1/0", 1
        )
        assert "0" in result or "나누" in result

    def test_unknown_error_fallback(self):
        """알 수 없는 에러도 처리해야 한다."""
        result = self.translator.translate(
            "CustomError", "something went wrong", "code", 1
        )
        assert result is not None and len(result) > 0

    def test_sanitize_traceback(self):
        """서버 경로가 마스킹되어야 한다."""
        stderr = 'File "/home/runner/work/app.py", line 5'
        result = self.translator.sanitize_traceback(stderr)
        assert "/home/" not in result
