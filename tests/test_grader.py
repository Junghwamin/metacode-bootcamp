"""채점기 테스트."""

from core.grader import Grader, GradeMethod, GradeResult


class TestGrader:
    """Grader 테스트."""

    def setup_method(self):
        """각 테스트 전 채점기 초기화."""
        self.grader = Grader()

    def test_grade_method_enum(self):
        """GradeMethod 열거형이 8가지 방식을 포함해야 한다."""
        methods = [m.value for m in GradeMethod]
        assert "exact_output" in methods
        assert "regex_output" in methods
        assert "variable_check" in methods
        assert "function_exists" in methods
        assert "function_call" in methods
        assert "class_check" in methods
        assert "multi_testcase" in methods
        assert "numeric_output" in methods

    def test_grade_result_dataclass(self):
        """GradeResult가 올바른 필드를 가져야 한다."""
        result = GradeResult(
            passed=True,
            score=1.0,
            total_tests=1,
            passed_tests=1,
            feedback="정답입니다!",
            details=[]
        )
        assert result.passed is True
        assert result.score == 1.0
        assert result.feedback == "정답입니다!"

    def test_normalize_output(self):
        """출력 정규화가 동작해야 한다."""
        assert self.grader._normalize_output("  hello  \n") == "hello"
        assert self.grader._normalize_output("a\n\n\nb") == "a\nb"
