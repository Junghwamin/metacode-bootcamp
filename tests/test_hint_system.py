"""힌트 시스템 테스트."""

from core.hint_system import HintSystem


class TestHintSystem:
    """HintSystem 테스트."""

    def setup_method(self):
        """각 테스트 전 힌트 시스템 초기화."""
        self.hint = HintSystem()

    def test_score_multiplier_no_hints(self):
        """힌트 미사용 시 1.2배 보너스."""
        assert self.hint.get_score_multiplier(0) == 1.2

    def test_score_multiplier_one_hint(self):
        """힌트 1개 사용 시 1.0배."""
        assert self.hint.get_score_multiplier(1) == 1.0

    def test_score_multiplier_two_hints(self):
        """힌트 2개 사용 시 0.9배."""
        assert self.hint.get_score_multiplier(2) == 0.9

    def test_score_multiplier_three_hints(self):
        """힌트 3개 사용 시 0.7배."""
        assert self.hint.get_score_multiplier(3) == 0.7

    def test_get_hint_returns_text(self):
        """유효한 힌트 레벨에서 텍스트를 반환해야 한다."""
        problem = {
            "hints": [
                {"level": 1, "text": "힌트1"},
                {"level": 2, "text": "힌트2"},
                {"level": 3, "text": "힌트3"},
            ]
        }
        result1 = self.hint.get_hint(problem, 1)
        result2 = self.hint.get_hint(problem, 2)
        result3 = self.hint.get_hint(problem, 3)
        # get_hint는 힌트 dict 또는 텍스트를 반환할 수 있음
        text1 = result1["text"] if isinstance(result1, dict) else result1
        text2 = result2["text"] if isinstance(result2, dict) else result2
        text3 = result3["text"] if isinstance(result3, dict) else result3
        assert text1 == "힌트1"
        assert text2 == "힌트2"
        assert text3 == "힌트3"

    def test_get_hint_invalid_level(self):
        """유효하지 않은 레벨에서 None을 반환해야 한다."""
        problem = {"hints": [{"level": 1, "text": "힌트1"}]}
        assert self.hint.get_hint(problem, 4) is None

    def test_should_show_answer(self):
        """힌트 3개 + 5회 시도 후 정답 공개."""
        assert self.hint.should_show_answer(3, 5) is True
        assert self.hint.should_show_answer(2, 5) is False
        assert self.hint.should_show_answer(3, 4) is False
