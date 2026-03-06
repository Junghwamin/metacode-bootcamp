"""자동 채점 시스템.

8가지 채점 방식(EXACT_OUTPUT, REGEX_OUTPUT, VARIABLE_CHECK,
FUNCTION_EXISTS, FUNCTION_CALL, CLASS_CHECK, MULTI_TESTCASE, NUMERIC_OUTPUT)을 지원하며,
부분 점수와 한국어 피드백을 제공한다.
"""
from dataclasses import dataclass, field
from enum import Enum
import re
import math


class GradeMethod(Enum):
    """채점 방식 열거형.

    각 방식은 문제 유형에 따라 선택된다:
    - EXACT_OUTPUT: 출력 문자열 정확 일치 (기초 print 문제)
    - REGEX_OUTPUT: 정규식 패턴 매칭 (형식 검증)
    - VARIABLE_CHECK: 변수 값 검사 (변수 할당 문제)
    - FUNCTION_EXISTS: 함수 정의 여부 (함수 선언 문제)
    - FUNCTION_CALL: 함수 호출 결과 검증 (함수 구현 문제)
    - CLASS_CHECK: 클래스 구조 및 동작 검증 (OOP 문제)
    - MULTI_TESTCASE: 여러 입력에 대한 출력 검증 (입출력 문제)
    - NUMERIC_OUTPUT: 부동소수점 출력 검증 (수치 계산 문제)
    """

    EXACT_OUTPUT = "exact_output"
    REGEX_OUTPUT = "regex_output"
    VARIABLE_CHECK = "variable_check"
    FUNCTION_EXISTS = "function_exists"
    FUNCTION_CALL = "function_call"
    CLASS_CHECK = "class_check"
    MULTI_TESTCASE = "multi_testcase"
    NUMERIC_OUTPUT = "numeric_output"


@dataclass
class GradeResult:
    """채점 결과.

    Attributes:
        passed: 최종 합격 여부 (score >= 1.0이거나 단일 통과 기준 충족)
        score: 획득 점수 (0.0 ~ 1.0, 부분 점수 포함)
        total_tests: 총 테스트케이스 수
        passed_tests: 통과한 테스트케이스 수
        feedback: 한국어 피드백 메시지
        details: 각 테스트케이스별 상세 결과 리스트
    """

    passed: bool
    score: float  # 0.0 ~ 1.0
    total_tests: int
    passed_tests: int
    feedback: str  # 한국어 피드백
    details: list = field(default_factory=list)


class Grader:
    """자동 채점기.

    문제 딕셔너리의 grading 설정에 따라 적절한 채점 방식을 선택하고
    GradeResult를 반환한다. 부분 점수와 한국어 피드백을 제공한다.

    Args:
        executor: 코드 실행기 인스턴스 (FUNCTION_CALL, CLASS_CHECK,
                  MULTI_TESTCASE 방식에서 사용). None이면 해당 방식 사용 불가.

    Example:
        >>> grader = Grader(executor=my_executor)
        >>> result = grader.grade(user_code, problem, execution_result)
        >>> print(result.feedback)
    """

    def __init__(self, executor=None):
        """채점기를 초기화한다.

        Args:
            executor: 코드 실행기. FUNCTION_CALL, CLASS_CHECK, MULTI_TESTCASE
                      채점 방식에서 추가 코드를 실행할 때 사용된다.
        """
        self.executor = executor

    def grade(self, user_code: str, problem: dict, execution_result=None) -> GradeResult:
        """문제를 채점한다.

        problem["grading"]["method"]에 따라 적절한 채점 메서드를 호출한다.
        execution_result가 None이고 executor가 있으면 코드를 실행한다.

        Args:
            user_code: 사용자가 작성한 파이썬 코드 문자열
            problem: 문제 딕셔너리. "grading" 키에 채점 설정 포함.
                     예: {"grading": {"method": "exact_output", "expected": "Hello"}}
            execution_result: 사전 실행된 결과 딕셔너리 (없으면 executor로 실행).
                              {"stdout": str, "stderr": str, "variables": dict, "error": str}

        Returns:
            GradeResult: 채점 결과 (passed, score, feedback, details 포함)

        Raises:
            ValueError: 지원하지 않는 채점 방식인 경우
        """
        grading_config = problem.get("grading", {})
        method_str = grading_config.get("method", GradeMethod.EXACT_OUTPUT.value)

        # 채점 방식 파싱
        try:
            method = GradeMethod(method_str)
        except ValueError:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=f"알 수 없는 채점 방식입니다: {method_str}",
            )

        # MULTI_TESTCASE는 user_code를 직접 사용 (실행 결과 불필요)
        if method == GradeMethod.MULTI_TESTCASE:
            test_cases = grading_config.get("test_cases", [])
            normalize = grading_config.get("normalize_whitespace", grading_config.get("normalize", True))
            return self._grade_multi_testcase(user_code, test_cases, normalize)

        # 그 외 방식: execution_result 필요
        if execution_result is None:
            if self.executor is not None:
                stdin = grading_config.get("test_input") or grading_config.get("stdin", "")
                if isinstance(stdin, list):
                    preset_inputs = [str(s) for s in stdin]
                elif stdin:
                    preset_inputs = stdin.split("\n")
                else:
                    preset_inputs = None
                # 챕터 6 문제에 preset_files가 있으면 VFS에 전달
                preset_files = problem.get("preset_files") if problem else None
                execution_result = self.executor.execute(
                    user_code,
                    preset_inputs=preset_inputs,
                    preset_files=preset_files if preset_files else None,
                )
            else:
                return GradeResult(
                    passed=False,
                    score=0.0,
                    total_tests=1,
                    passed_tests=0,
                    feedback="코드 실행 결과가 없습니다. 먼저 코드를 실행해주세요.",
                )

        # 실행 중 에러 확인
        # FUNCTION_CALL, CLASS_CHECK는 _grade_function_call/_grade_class_check에서
        # user_code를 재실행하므로 초기 실행 에러가 있어도 채점을 계속 진행한다.
        if execution_result.get("error_type") and method not in (
            GradeMethod.FUNCTION_EXISTS,
            GradeMethod.VARIABLE_CHECK,
            GradeMethod.FUNCTION_CALL,
            GradeMethod.CLASS_CHECK,
        ):
            error_msg = execution_result.get("stderr", "")
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=f"코드 실행 중 오류가 발생했습니다:\n\n{error_msg}",
            )

        # 채점 방식별 분기
        if method == GradeMethod.EXACT_OUTPUT:
            expected = grading_config.get("expected_output") or grading_config.get("expected", "")
            normalize = grading_config.get("normalize_whitespace", grading_config.get("normalize", True))
            return self._grade_exact_output(execution_result, expected, normalize)

        elif method == GradeMethod.REGEX_OUTPUT:
            pattern = grading_config.get("pattern", "")
            return self._grade_regex_output(execution_result, pattern)

        elif method == GradeMethod.VARIABLE_CHECK:
            expected_vars = grading_config.get("expected_vars", {})
            return self._grade_variable_check(execution_result, expected_vars)

        elif method == GradeMethod.FUNCTION_EXISTS:
            func_name = grading_config.get("func_name", "")
            return self._grade_function_exists(execution_result, func_name)

        elif method == GradeMethod.FUNCTION_CALL:
            func_name = grading_config.get("func_name", "")
            test_cases = grading_config.get("test_cases", [])
            # user_code를 재실행에 사용하기 위해 result에 주입
            if isinstance(execution_result, dict):
                execution_result["_user_code"] = user_code
            else:
                # ExecutionResult 객체인 경우 임시 dict로 래핑
                execution_result = dict(
                    stdout=execution_result.get("stdout", ""),
                    stderr=execution_result.get("stderr", ""),
                    variables=execution_result.get("variables", {}),
                    error_type=execution_result.get("error_type"),
                    _user_code=user_code,
                )
            return self._grade_function_call(execution_result, func_name, test_cases)

        elif method == GradeMethod.CLASS_CHECK:
            class_spec = grading_config.get("class_spec", {})
            # user_code를 재실행에 사용하기 위해 result에 주입
            if isinstance(execution_result, dict):
                execution_result["_user_code"] = user_code
            else:
                execution_result = dict(
                    stdout=execution_result.get("stdout", ""),
                    stderr=execution_result.get("stderr", ""),
                    variables=execution_result.get("variables", {}),
                    error_type=execution_result.get("error_type"),
                    _user_code=user_code,
                )
            return self._grade_class_check(execution_result, class_spec)

        elif method == GradeMethod.NUMERIC_OUTPUT:
            expected = grading_config.get("expected_output") or grading_config.get("expected", 0.0)
            epsilon = grading_config.get("tolerance", grading_config.get("epsilon", 1e-6))
            return self._grade_numeric_output(execution_result, expected, epsilon)

        else:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=f"지원하지 않는 채점 방식입니다: {method}",
            )

    # =========================================================================
    # 채점 메서드들
    # =========================================================================

    def _grade_exact_output(
        self, result: dict, expected: str, normalize: bool = True
    ) -> GradeResult:
        """출력 정확 일치 채점.

        실제 출력과 기대 출력을 비교한다. normalize=True이면 공백을 정규화한다.

        Args:
            result: 코드 실행 결과 딕셔너리 {"stdout": str, ...}
            expected: 기대 출력 문자열
            normalize: True이면 공백 정규화 후 비교 (기본값 True)

        Returns:
            GradeResult: 일치하면 passed=True, score=1.0
        """
        actual = result.get("stdout", "")

        if normalize:
            actual_cmp = self._normalize_output(actual)
            expected_cmp = self._normalize_output(expected)
        else:
            actual_cmp = actual
            expected_cmp = expected

        if actual_cmp == expected_cmp:
            return GradeResult(
                passed=True,
                score=1.0,
                total_tests=1,
                passed_tests=1,
                feedback="정답입니다! 훌륭해요! 🎉",
            )
        else:
            feedback = (
                f"기대 출력:\n{expected}\n\n"
                f"실제 출력:\n{actual}\n\n"
                f"차이점을 확인해보세요."
            )
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=feedback,
            )

    def _grade_regex_output(self, result: dict, pattern: str) -> GradeResult:
        """정규식 매칭 채점.

        실제 출력이 주어진 정규식 패턴과 매칭되는지 확인한다.

        Args:
            result: 코드 실행 결과 딕셔너리 {"stdout": str, ...}
            pattern: 매칭할 정규식 패턴 문자열

        Returns:
            GradeResult: 패턴 매칭이면 passed=True, score=1.0
        """
        actual = result.get("stdout", "")

        try:
            if re.search(pattern, actual, re.MULTILINE | re.DOTALL):
                return GradeResult(
                    passed=True,
                    score=1.0,
                    total_tests=1,
                    passed_tests=1,
                    feedback="정답입니다! 훌륭해요! 🎉",
                )
            else:
                return GradeResult(
                    passed=False,
                    score=0.0,
                    total_tests=1,
                    passed_tests=0,
                    feedback=(
                        f"출력이 기대 형식과 다릅니다.\n\n"
                        f"실제 출력:\n{actual}\n\n"
                        f"출력 형식을 다시 확인해보세요."
                    ),
                )
        except re.error as e:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=f"채점 패턴 오류입니다 (관리자에게 문의): {e}",
            )

    def _grade_variable_check(self, result: dict, expected_vars: dict) -> GradeResult:
        """변수 값 검사 채점.

        실행 후 변수들의 값을 기대값과 비교한다. 부분 점수를 지원한다.
        맞은 변수 수 / 전체 변수 수 = 점수.

        Args:
            result: 코드 실행 결과 딕셔너리 {"variables": dict, ...}
            expected_vars: 검사할 변수명과 기대값의 딕셔너리
                           예: {"x": 10, "name": "홍길동"}

        Returns:
            GradeResult: 부분 점수 포함. 모두 맞으면 score=1.0
        """
        actual_vars = result.get("variables", {})
        total = len(expected_vars)

        if total == 0:
            return GradeResult(
                passed=True,
                score=1.0,
                total_tests=0,
                passed_tests=0,
                feedback="검사할 변수가 없습니다.",
            )

        passed_count = 0
        details = []

        for var_name, expected_val in expected_vars.items():
            if var_name not in actual_vars:
                details.append(f"변수 '{var_name}'이(가) 정의되지 않았습니다.")
                continue

            actual_val = actual_vars[var_name]

            # 숫자 타입은 float 변환 후 비교 (정수/실수 혼용 허용)
            try:
                if isinstance(expected_val, (int, float)) and isinstance(
                    actual_val, (int, float)
                ):
                    if math.isclose(float(actual_val), float(expected_val), rel_tol=1e-6):
                        passed_count += 1
                        details.append(f"변수 '{var_name}': 정답 ({actual_val})")
                    else:
                        details.append(
                            f"변수 '{var_name}': 오답 "
                            f"(기대: {expected_val}, 실제: {actual_val})"
                        )
                elif actual_val == expected_val:
                    passed_count += 1
                    details.append(f"변수 '{var_name}': 정답 ({actual_val})")
                else:
                    details.append(
                        f"변수 '{var_name}': 오답 "
                        f"(기대: {expected_val!r}, 실제: {actual_val!r})"
                    )
            except Exception:
                # 비교 자체가 실패하면 불일치로 처리
                details.append(
                    f"변수 '{var_name}': 비교 실패 "
                    f"(기대: {expected_val!r}, 실제: {actual_val!r})"
                )

        score = passed_count / total
        passed = passed_count == total

        if passed:
            feedback = "정답입니다! 모든 변수의 값이 올바릅니다! 🎉"
        elif passed_count > 0:
            feedback = (
                f"{total}개 중 {passed_count}개 변수가 올바릅니다.\n\n"
                + "\n".join(details)
            )
        else:
            feedback = "변수 값이 올바르지 않습니다.\n\n" + "\n".join(details)

        return GradeResult(
            passed=passed,
            score=score,
            total_tests=total,
            passed_tests=passed_count,
            feedback=feedback,
            details=details,
        )

    def _grade_function_exists(self, result: dict, func_name: str) -> GradeResult:
        """함수 정의 여부 채점.

        실행 결과의 variables에서 해당 이름의 callable이 있는지 확인한다.

        Args:
            result: 코드 실행 결과 딕셔너리 {"variables": dict, ...}
            func_name: 확인할 함수 이름 문자열

        Returns:
            GradeResult: 함수가 정의되어 있으면 passed=True, score=1.0
        """
        variables = result.get("variables", {})

        # variables 딕셔너리에서 callable 여부 확인
        # executor가 직렬화한 경우 "__callable__" 플래그로 표시될 수 있음
        if func_name in variables:
            val = variables[func_name]
            # 직렬화된 함수 정보 처리: callable 표시 또는 실제 callable
            is_callable = (
                callable(val)
                or (isinstance(val, dict) and val.get("__callable__"))
                or (isinstance(val, str) and val.startswith("<function"))
            )
            if is_callable:
                return GradeResult(
                    passed=True,
                    score=1.0,
                    total_tests=1,
                    passed_tests=1,
                    feedback=f"정답입니다! '{func_name}' 함수가 올바르게 정의되었습니다! 🎉",
                )

        return GradeResult(
            passed=False,
            score=0.0,
            total_tests=1,
            passed_tests=0,
            feedback=(
                f"'{func_name}' 함수를 찾을 수 없습니다.\n\n"
                f"`def {func_name}(...):`로 함수를 정의했는지 확인해보세요."
            ),
        )

    def _grade_function_call(
        self, result: dict, func_name: str, test_cases: list
    ) -> GradeResult:
        """함수 호출 결과 검증 채점.

        executor로 user_code + 테스트 호출 코드를 재실행하여
        _test_result 변수에서 반환값을 추출한다.
        executor가 없으면 실패를 반환한다.

        Args:
            result: 코드 실행 결과 딕셔너리.
                    "_user_code" 키에 사용자 코드가 담겨 있어야 함.
            func_name: 호출할 함수 이름
            test_cases: 테스트케이스 리스트.
                        각 항목: {"args": [...], "kwargs": {...}, "expected": 값}

        Returns:
            GradeResult: 부분 점수 포함. 모두 통과하면 score=1.0

        Note:
            - executor가 None이면 채점 불가 에러를 반환한다.
            - 함수 반환값은 _test_result 변수로 추출한다.
            - 튜플 반환은 JSON 직렬화 시 리스트로 변환되므로 expected도 리스트 비교 지원.
        """
        total = len(test_cases)

        if total == 0:
            return GradeResult(
                passed=True,
                score=1.0,
                total_tests=0,
                passed_tests=0,
                feedback="테스트케이스가 없습니다.",
            )

        # executor 없으면 채점 불가
        if self.executor is None:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=total,
                passed_tests=0,
                feedback="FUNCTION_CALL 채점에는 executor가 필요합니다.",
            )

        # user_code 추출 (grade()에서 주입됨)
        user_code = result.get("_user_code", "")

        # 함수 존재 여부 확인
        # 우선 초기 실행 결과(variables)에서 확인하고,
        # variables에 없으면 user_code 소스에서 def 선언 패턴으로 확인한다.
        # (재귀 함수 등 executor 스코프 이슈로 초기 실행이 실패했을 때도 처리)
        variables = result.get("variables", {})
        func_val = variables.get(func_name)
        func_exists = (
            callable(func_val)
            or (isinstance(func_val, dict) and func_val.get("__callable__"))
            or (isinstance(func_val, str) and (
                func_val.startswith("<function") or func_val.startswith("<class")
            ))
        )
        # variables에서 찾지 못한 경우 user_code 텍스트에서 def 선언 확인
        if not func_exists and user_code:
            import re as _re
            func_exists = bool(
                _re.search(r"^\s*def\s+" + _re.escape(func_name) + r"\s*\(", user_code, _re.MULTILINE)
            )
        if not func_exists:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=total,
                passed_tests=0,
                feedback=(
                    f"'{func_name}' 함수를 찾을 수 없습니다.\n\n"
                    f"함수가 올바르게 정의되었는지 확인해보세요."
                ),
            )

        passed_count = 0
        details = []

        for i, tc in enumerate(test_cases, 1):
            args = tc.get("args", [])
            kwargs = tc.get("kwargs", {})
            expected = tc.get("expected")

            try:
                # Step 1: 호출 코드 생성
                # args를 repr()로 직렬화하여 코드에 삽입
                # kwargs가 있는 경우 **kwargs 형태로 삽입
                args_repr = ", ".join(repr(a) for a in args)
                kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
                call_args = ", ".join(filter(None, [args_repr, kwargs_repr]))
                # metacode_result: _로 시작하지 않아야 executor 변수 추출에 포함됨
                call_snippet = f"metacode_result = {func_name}({call_args})\n"

                # Step 2: user_code + 테스트 호출 코드를 합쳐서 실행
                combined_code = user_code + "\n" + call_snippet
                exec_result = self.executor.execute(combined_code)

                # Step 3: 에러 확인
                if exec_result.get("error_type"):
                    details.append(
                        f"테스트 {i}: 실행 오류 "
                        f"(입력: {args}{' ' + str(kwargs) if kwargs else ''}, "
                        f"오류: {exec_result.get('stderr', '')[:80]})"
                    )
                    continue

                # Step 4: metacode_result 변수 추출
                actual = exec_result.get("variables", {}).get("metacode_result")

                # Step 5: 결과 비교
                # 튜플은 JSON 직렬화 시 리스트가 되므로 expected가 list면 actual도 list와 비교
                if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                    match = math.isclose(float(actual), float(expected), rel_tol=1e-6)
                elif isinstance(expected, (list, tuple)) and isinstance(actual, list):
                    # 튜플 반환값 처리: expected를 list로 정규화 후 비교
                    match = list(expected) == actual
                else:
                    match = actual == expected

                if match:
                    passed_count += 1
                    details.append(
                        f"테스트 {i}: 통과 "
                        f"(입력: {args}{' ' + str(kwargs) if kwargs else ''}, "
                        f"출력: {actual})"
                    )
                else:
                    details.append(
                        f"테스트 {i}: 실패 "
                        f"(입력: {args}{' ' + str(kwargs) if kwargs else ''}, "
                        f"기대: {expected!r}, 실제: {actual!r})"
                    )

            except Exception as e:
                details.append(
                    f"테스트 {i}: 오류 발생 "
                    f"(입력: {args}, 오류: {type(e).__name__}: {e})"
                )

        score = passed_count / total
        passed = passed_count == total

        if passed:
            feedback = f"정답입니다! 모든 {total}개 테스트를 통과했습니다! 🎉"
        else:
            feedback = (
                f"{total}개 중 {passed_count}개 테스트를 통과했습니다.\n\n"
                + "\n".join(details)
            )

        return GradeResult(
            passed=passed,
            score=score,
            total_tests=total,
            passed_tests=passed_count,
            feedback=feedback,
            details=details,
        )

    def _grade_class_check(self, result: dict, class_spec: dict) -> GradeResult:
        """클래스 구조 및 동작 검증 채점.

        클래스 존재 → 메서드 존재 → 테스트케이스 실행 순서로 검증한다.
        executor로 user_code + 클래스 테스트 코드를 재실행하여 결과를 추출한다.

        검증 순서 (논리적 의존성):
        1. 클래스 정의 여부 (기본 점수 획득)
        2. 필수 메서드 존재 여부 - user_code + hasattr 코드 재실행
        3. 테스트케이스 실행 결과 - user_code + 인스턴스 생성 + 메서드 호출 재실행

        Args:
            result: 코드 실행 결과 딕셔너리.
                    "_user_code" 키에 사용자 코드가 담겨 있어야 함.
            class_spec: 클래스 검사 명세 딕셔너리
                        {"name": "클래스명", "methods": ["메서드명"], "test_cases": [...]}
                        test_cases 각 항목:
                          {"init_args": [...], "method": "메서드명",
                           "args": [...], "expected": 값}

        Returns:
            GradeResult: 부분 점수 포함. 모두 통과하면 score=1.0

        Note:
            - executor가 None이면 채점 불가 에러를 반환한다.
            - 클래스 존재는 직렬화된 "<class '...'>'" 문자열로도 감지한다.
            - 메서드 존재는 재실행 후 _test_has_{method} 변수로 확인한다.
            - 테스트 반환값은 _test_result 변수로 추출한다.
        """
        variables = result.get("variables", {})
        class_name = class_spec.get("name", "")
        required_methods = class_spec.get("methods", [])
        test_cases = class_spec.get("test_cases", [])

        details = []

        # executor 없으면 채점 불가
        if self.executor is None:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback="CLASS_CHECK 채점에는 executor가 필요합니다.",
            )

        # user_code 추출 (grade()에서 주입됨)
        user_code = result.get("_user_code", "")

        # Step 1: 클래스 존재 확인
        # executor가 직렬화한 클래스는 "<class 'ClassName'>" 형태의 문자열.
        # variables에서 찾지 못한 경우 user_code 텍스트에서 class 선언 확인.
        cls_val = variables.get(class_name)
        class_exists = (
            (isinstance(cls_val, str) and cls_val.startswith("<class"))
            or isinstance(cls_val, type)
        )
        # variables에서 찾지 못한 경우 user_code 텍스트에서 class 선언 확인
        if not class_exists and user_code:
            import re as _re
            class_exists = bool(
                _re.search(r"^\s*class\s+" + _re.escape(class_name) + r"\s*[\(:]", user_code, _re.MULTILINE)
            )
        if not class_exists:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=(
                    f"'{class_name}' 클래스를 찾을 수 없습니다.\n\n"
                    f"`class {class_name}:` 로 클래스를 정의했는지 확인해보세요."
                ),
            )

        # 클래스 존재 자체를 1점으로 인정
        class_exists_score = 1
        details.append(f"'{class_name}' 클래스 정의: 확인됨")

        # Step 2: 필수 메서드 존재 확인
        # user_code + hasattr 체크 코드를 재실행하여 metacode_has_{idx} 변수로 확인
        # 주의: 변수명이 _로 시작하면 executor가 추출하지 않으므로 metacode_ 접두사 사용
        method_passed = 0
        if required_methods:
            method_check_lines = []
            for idx, method_name in enumerate(required_methods):
                # hasattr로 메서드 존재 여부를 변수에 저장
                # 변수명에 인덱스 사용: 메서드명에 특수문자 없어도 일관성 유지
                method_check_lines.append(
                    f"metacode_has_{idx} = hasattr({class_name}, '{method_name}') "
                    f"and callable(getattr({class_name}, '{method_name}', None))"
                )
            combined_code = user_code + "\n" + "\n".join(method_check_lines) + "\n"
            check_result = self.executor.execute(combined_code)
            check_vars = check_result.get("variables", {})

            for idx, method_name in enumerate(required_methods):
                has_method = check_vars.get(f"metacode_has_{idx}", False)
                if has_method:
                    method_passed += 1
                    details.append(f"메서드 '{method_name}': 존재")
                else:
                    details.append(f"메서드 '{method_name}': 없음")

        # Step 3: 테스트케이스 실행
        # user_code + 인스턴스 생성 + 메서드 호출 코드를 재실행
        tc_passed = 0
        tc_total = len(test_cases)

        for i, tc in enumerate(test_cases, 1):
            init_args = tc.get("init_args", [])
            method_name = tc.get("method", "")
            args = tc.get("args", [])
            kwargs = tc.get("kwargs", {})
            expected = tc.get("expected")

            try:
                # 인스턴스 생성 코드
                init_args_repr = ", ".join(repr(a) for a in init_args)
                args_repr = ", ".join(repr(a) for a in args)
                kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
                call_args = ", ".join(filter(None, [args_repr, kwargs_repr]))

                # metacode_obj, metacode_result: _로 시작하지 않아야 executor 추출에 포함됨
                test_snippet = (
                    f"metacode_obj = {class_name}({init_args_repr})\n"
                    f"metacode_result = metacode_obj.{method_name}({call_args})\n"
                )
                combined_code = user_code + "\n" + test_snippet
                exec_result = self.executor.execute(combined_code)

                # 에러 확인
                if exec_result.get("error_type"):
                    details.append(
                        f"테스트 {i} ({method_name}): 실행 오류 "
                        f"({exec_result.get('stderr', '')[:80]})"
                    )
                    continue

                # metacode_result 변수 추출
                actual = exec_result.get("variables", {}).get("metacode_result")

                # 결과 비교
                # expected가 None인 경우 (반환값 검사 없이 오류 없이 실행만 확인)
                if expected is None:
                    tc_passed += 1
                    details.append(
                        f"테스트 {i} ({method_name}): 통과 "
                        f"(오류 없이 실행됨)"
                    )
                elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                    match = math.isclose(float(actual), float(expected), rel_tol=1e-6)
                    if match:
                        tc_passed += 1
                        details.append(f"테스트 {i} ({method_name}): 통과 (결과: {actual})")
                    else:
                        details.append(
                            f"테스트 {i} ({method_name}): 실패 "
                            f"(기대: {expected!r}, 실제: {actual!r})"
                        )
                else:
                    if actual == expected:
                        tc_passed += 1
                        details.append(f"테스트 {i} ({method_name}): 통과 (결과: {actual})")
                    else:
                        details.append(
                            f"테스트 {i} ({method_name}): 실패 "
                            f"(기대: {expected!r}, 실제: {actual!r})"
                        )

            except Exception as e:
                details.append(
                    f"테스트 {i} ({method_name}): 오류 "
                    f"({type(e).__name__}: {e})"
                )

        # 부분 점수 계산
        # 클래스 존재: 30%, 메서드 존재: 30%, 테스트케이스: 40%
        total_weight = 0
        score = 0.0

        # 클래스 존재 점수 (항상 기여)
        score += 0.3 * class_exists_score
        total_weight += 0.3

        # 메서드 존재 점수
        if required_methods:
            method_ratio = method_passed / len(required_methods)
            score += 0.3 * method_ratio
            total_weight += 0.3

        # 테스트케이스 점수
        if tc_total > 0:
            tc_ratio = tc_passed / tc_total
            score += 0.4 * tc_ratio
            total_weight += 0.4

        # 가중치 정규화 (메서드/테스트케이스 없는 경우 대비)
        if total_weight > 0 and total_weight < 1.0:
            score = score / total_weight

        score = min(1.0, score)
        passed = score >= 1.0 or (
            class_exists_score
            and (not required_methods or method_passed == len(required_methods))
            and (tc_total == 0 or tc_passed == tc_total)
        )

        if passed:
            feedback = f"정답입니다! '{class_name}' 클래스가 올바르게 구현되었습니다! 🎉"
        else:
            feedback = (
                f"클래스 구현에 문제가 있습니다 (점수: {score:.0%}).\n\n"
                + "\n".join(details)
            )

        return GradeResult(
            passed=passed,
            score=score,
            total_tests=1 + len(required_methods) + tc_total,
            passed_tests=class_exists_score + method_passed + tc_passed,
            feedback=feedback,
            details=details,
        )

    def _grade_multi_testcase(
        self, user_code: str, test_cases: list, normalize: bool = True
    ) -> GradeResult:
        """여러 입력에 대한 출력 검증 채점.

        각 테스트케이스마다 사용자 코드를 별도로 실행하여 출력을 비교한다.
        executor를 사용하며 합산 타임아웃 10초를 적용한다.

        Args:
            user_code: 사용자가 작성한 파이썬 코드 문자열
            test_cases: 테스트케이스 리스트.
                        각 항목: {"stdin": str, "expected": str}
            normalize: True이면 출력 공백 정규화 후 비교 (기본값 True)

        Returns:
            GradeResult: 부분 점수 포함. 모두 통과하면 score=1.0
        """
        if self.executor is None:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=len(test_cases),
                passed_tests=0,
                feedback="MULTI_TESTCASE 채점에는 executor가 필요합니다.",
            )

        total = len(test_cases)
        if total == 0:
            return GradeResult(
                passed=True,
                score=1.0,
                total_tests=0,
                passed_tests=0,
                feedback="테스트케이스가 없습니다.",
            )

        passed_count = 0
        details = []

        for i, tc in enumerate(test_cases, 1):
            stdin = tc.get("input") or tc.get("stdin", "")
            expected = tc.get("expected_output") or tc.get("expected", "")

            try:
                if isinstance(stdin, list):
                    preset_inputs = [str(s) for s in stdin]
                elif stdin:
                    preset_inputs = stdin.split("\n")
                else:
                    preset_inputs = None
                exec_result = self.executor.execute(
                    user_code, preset_inputs=preset_inputs
                )

                actual = exec_result.get("stdout", "")

                if normalize:
                    actual_cmp = self._normalize_output(actual)
                    expected_cmp = self._normalize_output(expected)
                else:
                    actual_cmp = actual
                    expected_cmp = expected

                if actual_cmp == expected_cmp:
                    passed_count += 1
                    stdin_repr = repr(stdin)[:30]
                    actual_repr = repr(actual)[:30]
                    details.append(
                        f"테스트 {i}: 통과 "
                        f"(입력: {stdin_repr}, 출력: {actual_repr})"
                    )
                else:
                    stdin_repr = repr(stdin)[:30]
                    expected_repr = repr(expected)[:30]
                    actual_repr = repr(actual)[:30]
                    details.append(
                        f"테스트 {i}: 실패 "
                        f"(입력: {stdin_repr}, "
                        f"기대: {expected_repr}, 실제: {actual_repr})"
                    )

            except Exception as e:
                details.append(f"테스트 {i}: 실행 오류 ({type(e).__name__}: {e})")

        score = passed_count / total
        passed = passed_count == total

        if passed:
            feedback = f"정답입니다! 모든 {total}개 테스트를 통과했습니다! 🎉"
        else:
            feedback = (
                f"{total}개 중 {passed_count}개 테스트를 통과했습니다.\n\n"
                + "\n".join(details)
            )

        return GradeResult(
            passed=passed,
            score=score,
            total_tests=total,
            passed_tests=passed_count,
            feedback=feedback,
            details=details,
        )

    def _grade_numeric_output(
        self, result: dict, expected: float, epsilon: float = 1e-6
    ) -> GradeResult:
        """부동소수점 출력 검증 채점.

        stdout의 마지막 의미 있는 줄을 float으로 파싱하여 비교한다.
        abs(actual - expected) < epsilon이면 통과.

        Args:
            result: 코드 실행 결과 딕셔너리 {"stdout": str, ...}
            expected: 기대 수치 (int 또는 float)
            epsilon: 허용 오차 (기본값 1e-6). 절대 오차 기준.

        Returns:
            GradeResult: 오차 범위 내이면 passed=True, score=1.0
        """
        stdout = result.get("stdout", "").strip()

        if not stdout:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=(
                    "출력이 없습니다.\n\n"
                    "계산 결과를 `print()`로 출력했는지 확인해보세요."
                ),
            )

        # 마지막 의미 있는 줄에서 숫자 파싱
        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        last_line = lines[-1] if lines else ""

        try:
            actual = float(last_line)
        except ValueError:
            # 마지막 줄 전체가 숫자가 아니면 숫자만 추출 시도
            numbers = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", last_line)
            if numbers:
                try:
                    actual = float(numbers[-1])
                except ValueError:
                    return GradeResult(
                        passed=False,
                        score=0.0,
                        total_tests=1,
                        passed_tests=0,
                        feedback=(
                            f"출력에서 숫자를 파싱할 수 없습니다.\n\n"
                            f"실제 출력: {stdout}\n\n"
                            f"숫자 값을 출력하도록 코드를 수정해보세요."
                        ),
                    )
            else:
                return GradeResult(
                    passed=False,
                    score=0.0,
                    total_tests=1,
                    passed_tests=0,
                    feedback=(
                        f"출력에서 숫자를 찾을 수 없습니다.\n\n"
                        f"실제 출력: {stdout}"
                    ),
                )

        # expected가 문자열이면 숫자 추출
        try:
            expected_val = float(expected)
        except (ValueError, TypeError):
            nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(expected))
            expected_val = float(nums[-1]) if nums else 0.0

        # 절대 오차 비교
        if abs(actual - expected_val) < epsilon:
            return GradeResult(
                passed=True,
                score=1.0,
                total_tests=1,
                passed_tests=1,
                feedback=f"정답입니다! 계산 결과가 올바릅니다 ({actual})! 🎉",
            )
        else:
            return GradeResult(
                passed=False,
                score=0.0,
                total_tests=1,
                passed_tests=0,
                feedback=(
                    f"계산 결과가 다릅니다.\n\n"
                    f"기대값: {expected}\n"
                    f"실제값: {actual}\n"
                    f"차이: {abs(actual - expected_val):.2e}\n\n"
                    f"수식과 계산 과정을 다시 확인해보세요."
                ),
            )

    # =========================================================================
    # 유틸리티 메서드
    # =========================================================================

    def _normalize_output(self, text: str) -> str:
        """출력 문자열을 정규화한다.

        trailing whitespace 제거, 빈 줄 무시, 전체 strip을 적용한다.
        EXACT_OUTPUT과 MULTI_TESTCASE 채점에서 사용된다.

        Args:
            text: 정규화할 출력 문자열

        Returns:
            str: 정규화된 문자열
                 - 각 줄의 앞뒤 공백 제거
                 - 빈 줄 제거
                 - 전체 앞뒤 공백 제거
        """
        if not text:
            return ""

        # 각 줄의 trailing whitespace 제거 후 빈 줄 제거
        lines = [line.strip() for line in text.splitlines()]
        non_empty_lines = [line for line in lines if line]

        return "\n".join(non_empty_lines).strip()
