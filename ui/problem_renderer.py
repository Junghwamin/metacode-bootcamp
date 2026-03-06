"""실습 문제 렌더링 모듈.

문제 설명 → 코드 에디터 → 실행/제출 → 채점 결과 → 힌트의 플로우.

학습자 경험 설계 원칙:
    - 실행 버튼: 즉각적인 피드백 (제출 없이 코드 테스트 가능)
    - 제출 버튼: 공식 채점 + 진행도 업데이트
    - 초기화 버튼: 실수를 두려워하지 않도록 언제든 initial_code로 복귀
    - 힌트 패널: 보상 프레이밍으로 자율 학습 동기 유지
"""

import streamlit as st

from ui.components import (
    render_code_editor,
    render_difficulty_badge,
    render_execution_result,
    render_grade_result,
    render_hint_panel,
    render_problem_navigation,
)


class ProblemRenderer:
    """실습 문제 렌더러.

    챕터의 실습 문제 목록을 탐색하고, 선택된 문제를 렌더링한다.
    난이도 필터, 문제 선택, 코드 에디터, 실행/제출/초기화, 힌트를 통합한다.

    Attributes:
        chapter_id (int): 현재 챕터 번호
        problems (list[dict]): 전체 문제 목록
        progress_manager: 진행도 관리 객체 (optional)
        filtered_problems (list[dict]): 현재 필터 적용된 문제 목록

    session_state 키 규칙:
        - f"problem_code_{chapter_id}_{problem_id}": 문제별 현재 코드
        - f"problem_result_{chapter_id}_{problem_id}": 실행 결과
        - f"problem_grade_{chapter_id}_{problem_id}": 채점 결과
        - f"problem_hints_{chapter_id}_{problem_id}": 사용한 힌트 수
        - f"selected_problem_idx_{chapter_id}": 현재 선택된 문제 인덱스
        - f"difficulty_filter_{chapter_id}": 난이도 필터 상태 dict
    """

    def __init__(
        self,
        chapter_id: int,
        problems: list,
        progress_manager=None,
    ) -> None:
        """ProblemRenderer를 초기화한다.

        Args:
            chapter_id: 현재 챕터 번호
            problems: 문제 딕셔너리 목록.
                각 문제 구조: {
                    'id': str,
                    'title': str,
                    'difficulty': str,       # basic | intermediate | advanced
                    'description': str,      # 문제 설명 (마크다운)
                    'instructions': list[str], # 지시사항 목록
                    'initial_code': str,     # 시작 코드
                    'hints': list[str],      # 힌트 목록 (최대 3개)
                    'solution': str,         # 정답 코드
                    'related_section': str,  # 관련 개념 섹션 ID (optional)
                    'test_cases': list[dict], # 테스트 케이스 (optional)
                }
            progress_manager: 진행도 관리 객체. None이면 저장 생략.
        """
        self.chapter_id = chapter_id
        self.problems = problems or []
        self.progress_manager = progress_manager
        self.filtered_problems = list(self.problems)

        # 난이도 필터 초기화 (모두 활성화 상태)
        filter_key = f"difficulty_filter_{chapter_id}"
        if filter_key not in st.session_state:
            st.session_state[filter_key] = {
                "basic": True,
                "intermediate": True,
                "advanced": True,
            }

    def render(self) -> None:
        """전체 문제 UI를 렌더링한다.

        구조:
            1. 난이도 필터 (체크박스 행)
            2. 문제 선택 UI (라디오 또는 selectbox)
            3. 선택된 문제 렌더링

        난이도 필터 변경 시 즉시 문제 목록이 업데이트된다.
        """
        if not self.problems:
            st.info("등록된 실습 문제가 없습니다.")
            return

        # ---- 1. 난이도 필터 ----
        self._render_difficulty_filter()

        # 필터 적용
        self._apply_difficulty_filter()

        if not self.filtered_problems:
            st.warning("선택한 난이도에 해당하는 문제가 없습니다. 필터를 조정해 보세요.")
            return

        # ---- 2. 문제 선택 + 문제 렌더링 (좌우 분할 레이아웃) ----
        # 문제가 5개 이하면 사이드바 스타일, 많으면 셀렉트박스
        use_sidebar_style = len(self.filtered_problems) <= 8

        if use_sidebar_style:
            # 좌: 문제 목록 (1/3), 우: 문제 내용 (2/3)
            col_nav, col_content = st.columns([1, 2])

            with col_nav:
                current_idx = st.session_state.get(
                    f"selected_problem_idx_{self.chapter_id}", 0
                )
                # 인덱스 범위 보정
                current_idx = min(current_idx, len(self.filtered_problems) - 1)

                progress = self._get_progress_dict()
                new_idx = render_problem_navigation(
                    problems=self.filtered_problems,
                    current_idx=current_idx,
                    progress=progress,
                )

                # 인덱스 변경 감지 및 저장
                if new_idx != current_idx:
                    st.session_state[f"selected_problem_idx_{self.chapter_id}"] = new_idx

            with col_content:
                current_idx = st.session_state.get(
                    f"selected_problem_idx_{self.chapter_id}", 0
                )
                current_idx = min(current_idx, len(self.filtered_problems) - 1)
                selected_problem = self.filtered_problems[current_idx]
                self._render_problem(selected_problem)

        else:
            # 셀렉트박스로 선택
            current_idx = st.session_state.get(
                f"selected_problem_idx_{self.chapter_id}", 0
            )
            current_idx = min(current_idx, len(self.filtered_problems) - 1)

            problem_titles = [
                f"{i+1}. {p.get('title', '제목 없음')}"
                for i, p in enumerate(self.filtered_problems)
            ]
            selected_label = st.selectbox(
                "문제 선택",
                options=range(len(self.filtered_problems)),
                format_func=lambda i: problem_titles[i],
                index=current_idx,
                key=f"problem_selectbox_{self.chapter_id}",
            )
            if selected_label is not None:
                st.session_state[f"selected_problem_idx_{self.chapter_id}"] = selected_label
                self._render_problem(self.filtered_problems[selected_label])

        # 건너뛰기 플래그 처리 (힌트 패널에서 설정됨)
        if st.session_state.get("skip_to_next_problem", False):
            st.session_state["skip_to_next_problem"] = False
            current_idx = st.session_state.get(
                f"selected_problem_idx_{self.chapter_id}", 0
            )
            next_idx = min(current_idx + 1, len(self.filtered_problems) - 1)
            st.session_state[f"selected_problem_idx_{self.chapter_id}"] = next_idx
            st.rerun()

    def _render_difficulty_filter(self) -> None:
        """난이도 필터 체크박스를 렌더링한다.

        기초/중급/심화 세 가지 체크박스로 필터링.
        각 체크박스 옆에 해당 난이도의 문제 수를 표시한다.
        """
        filter_key = f"difficulty_filter_{self.chapter_id}"
        filters = st.session_state[filter_key]

        # 난이도별 문제 수 집계
        difficulty_counts = {"basic": 0, "intermediate": 0, "advanced": 0}
        for prob in self.problems:
            d = prob.get("difficulty", "basic")
            if d in difficulty_counts:
                difficulty_counts[d] += 1

        st.markdown("**난이도 필터:**")
        col1, col2, col3, _ = st.columns([1, 1, 1, 2])

        difficulty_cols = [
            (col1, "basic", "기초"),
            (col2, "intermediate", "중급"),
            (col3, "advanced", "심화"),
        ]

        for col, diff_key, diff_label in difficulty_cols:
            with col:
                count = difficulty_counts.get(diff_key, 0)
                # 체크박스 레이블에 문제 수 포함
                new_val = st.checkbox(
                    f"{diff_label} ({count})",
                    value=filters.get(diff_key, True),
                    key=f"filter_{self.chapter_id}_{diff_key}",
                )
                # 변경 감지
                if new_val != filters.get(diff_key, True):
                    st.session_state[filter_key][diff_key] = new_val
                    st.rerun()

    def _apply_difficulty_filter(self) -> None:
        """현재 필터 설정을 적용하여 filtered_problems를 업데이트한다.

        필터에서 선택된 난이도의 문제만 filtered_problems에 남긴다.
        모든 필터가 꺼진 경우 전체 문제를 표시한다 (usability).
        """
        filter_key = f"difficulty_filter_{self.chapter_id}"
        filters = st.session_state.get(filter_key, {})

        active_difficulties = {k for k, v in filters.items() if v}

        if not active_difficulties:
            # 모든 필터가 꺼지면 전체 표시 (빈 목록 방지)
            self.filtered_problems = list(self.problems)
        else:
            self.filtered_problems = [
                p for p in self.problems
                if p.get("difficulty", "basic") in active_difficulties
            ]

    def _render_problem(self, problem: dict) -> None:
        """선택된 단일 문제를 렌더링한다.

        렌더링 순서:
            1. 난이도 배지 + 제목
            2. 관련 개념 복습 링크 (related_section 필드)
            3. 문제 설명 + 지시사항
            4. 코드 에디터
            5. 버튼 행: [실행] [제출] [초기화]
            6. 실행 결과 영역
            7. 채점 결과 영역
            8. 힌트 패널

        Args:
            problem: 렌더링할 문제 딕셔너리
        """
        prob_id = problem.get("id", "unknown")
        title = problem.get("title", "문제")
        difficulty = problem.get("difficulty", "basic")
        description = problem.get("description", "")
        instructions = problem.get("instructions", [])
        initial_code = problem.get("initial_code", "# 여기에 코드를 작성하세요\n")
        related_section = problem.get("related_section", "")

        # session_state 키 정의 (문제별 고유)
        code_key = f"problem_code_{self.chapter_id}_{prob_id}"
        result_key = f"problem_result_{self.chapter_id}_{prob_id}"
        grade_key = f"problem_grade_{self.chapter_id}_{prob_id}"
        hints_key = f"problem_hints_{self.chapter_id}_{prob_id}"

        # 힌트 사용 횟수 초기화
        if hints_key not in st.session_state:
            st.session_state[hints_key] = 0

        # ---- 1. 난이도 배지 + 제목 ----
        col_title, col_badge = st.columns([4, 1])
        with col_title:
            st.markdown(f"### {title}")
        with col_badge:
            st.markdown("<br>", unsafe_allow_html=True)
            render_difficulty_badge(difficulty)

        # ---- 2. 관련 개념 복습 링크 ----
        if related_section:
            st.markdown(
                f"""
                <div style="background:#EBF8FF; border-radius:6px; padding:0.4rem 0.75rem;
                            font-size:0.88em; color:#2B6CB0; margin-bottom:0.5rem;">
                    📖 <strong>관련 개념:</strong> 개념 학습 탭의
                    <em>{related_section}</em> 섹션을 먼저 확인해 보세요.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---- 3. 문제 설명 + 지시사항 ----
        if description:
            st.markdown(description)

        if instructions:
            st.markdown("**지시사항:**")
            for i, instruction in enumerate(instructions, 1):
                st.markdown(f"{i}. {instruction}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- 4. 코드 에디터 ----
        # initial_code를 session_state에 보존하여 초기화 기능 구현
        if code_key not in st.session_state:
            st.session_state[code_key] = initial_code

        current_code = render_code_editor(
            key=f"editor_{self.chapter_id}_{prob_id}",
            initial_code=st.session_state[code_key],
            height=300,
        )

        # 에디터 변경 사항을 session_state에 동기화
        if current_code:
            st.session_state[code_key] = current_code

        # ---- 5. 버튼 행: [실행] [제출] [초기화] ----
        col_run, col_submit, col_reset, _ = st.columns([1, 1, 1, 1])

        with col_run:
            st.markdown('<div class="btn-run">', unsafe_allow_html=True)
            run_clicked = st.button(
                "▶ 실행",
                key=f"run_{self.chapter_id}_{prob_id}",
                use_container_width=True,
                help="코드를 실행하고 출력을 확인합니다 (채점 없음)",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_submit:
            st.markdown('<div class="btn-submit">', unsafe_allow_html=True)
            submit_clicked = st.button(
                "✓ 제출",
                key=f"submit_{self.chapter_id}_{prob_id}",
                use_container_width=True,
                help="코드를 제출하고 채점합니다. 통과하면 진행도가 저장됩니다.",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_reset:
            st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
            reset_clicked = st.button(
                "↺ 초기화",
                key=f"reset_{self.chapter_id}_{prob_id}",
                use_container_width=True,
                help="코드를 처음 상태로 되돌립니다.",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # ---- 버튼 액션 처리 ----
        self._handle_button_actions(
            run_clicked, submit_clicked, reset_clicked,
            code_key, result_key, grade_key, hints_key,
            initial_code, prob_id, problem,
        )

        # ---- 6. 실행 결과 영역 ----
        exec_result = st.session_state.get(result_key)
        if exec_result:
            render_execution_result(exec_result)

        # ---- 7. 채점 결과 영역 ----
        grade_result = st.session_state.get(grade_key)
        if grade_result:
            render_grade_result(grade_result)

        # ---- 8. 힌트 패널 ----
        hints_used = st.session_state.get(hints_key, 0)

        def on_hint_callback(hint_num: int) -> None:
            """힌트 열기 콜백.

            Args:
                hint_num: 열려는 힌트 번호 (1부터 시작)
            """
            st.session_state[hints_key] = hint_num
            st.rerun()

        render_hint_panel(
            problem=problem,
            hints_used=hints_used,
            on_hint_callback=on_hint_callback,
        )

    def _handle_button_actions(
        self,
        run_clicked: bool,
        submit_clicked: bool,
        reset_clicked: bool,
        code_key: str,
        result_key: str,
        grade_key: str,
        hints_key: str,
        initial_code: str,
        prob_id: str,
        problem: dict,
    ) -> None:
        """버튼 클릭 액션을 처리한다.

        실행/제출/초기화 버튼의 각 클릭 이벤트를 처리한다.

        Args:
            run_clicked: 실행 버튼 클릭 여부
            submit_clicked: 제출 버튼 클릭 여부
            reset_clicked: 초기화 버튼 클릭 여부
            code_key: 코드 session_state 키
            result_key: 실행 결과 session_state 키
            grade_key: 채점 결과 session_state 키
            hints_key: 힌트 사용 횟수 session_state 키
            initial_code: 초기 코드 문자열
            prob_id: 문제 ID
            problem: 문제 딕셔너리
        """
        if reset_clicked:
            # 초기화: 코드를 initial_code로 리셋
            st.session_state[code_key] = initial_code
            # code_editor의 내부 상태도 리셋
            editor_state_key = f"code_editor_{self.chapter_id}_{prob_id}"
            if editor_state_key in st.session_state:
                del st.session_state[editor_state_key]
            st.rerun()

        if run_clicked:
            # 실행: 코드 실행 후 결과 저장 (채점 없음)
            code_to_run = st.session_state.get(code_key, initial_code)
            result = self._execute_code(code_to_run)
            st.session_state[result_key] = result

        if submit_clicked:
            # 제출: 코드 실행 + 채점 + 진행도 업데이트
            code_to_submit = st.session_state.get(code_key, initial_code)
            result = self._execute_code(code_to_submit)
            st.session_state[result_key] = result

            if result.get("success", False):
                # 실행 성공 시에만 채점 진행
                hints_used = st.session_state.get(hints_key, 0)
                grade_result = self._grade_code(
                    code_to_submit, problem, hints_used
                )
                st.session_state[grade_key] = grade_result

                # 통과 시 진행도 업데이트
                if grade_result.get("passed", False):
                    self._update_progress(prob_id, grade_result)
                    st.balloons()  # 축하 애니메이션
            else:
                # 실행 실패 시 채점 결과 초기화
                st.session_state[grade_key] = None

    def _execute_code(self, code: str) -> dict:
        """코드를 안전하게 실행하고 결과를 반환한다.

        core/executor.py의 execute_code 함수를 사용한다.

        Args:
            code: 실행할 Python 코드 문자열

        Returns:
            dict: 실행 결과 딕셔너리
                성공: {'success': True, 'output': str}
                실패: {'success': False, 'error': str, 'error_type': str,
                       'translated': str}
        """
        try:
            from core.executor import execute_code  # type: ignore

            return execute_code(code, chapter_id=self.chapter_id)

        except ImportError:
            return {
                "success": False,
                "error": "코드 실행 엔진(core/executor.py)을 찾을 수 없습니다.",
                "error_type": "ImportError",
                "translated": "개발 환경을 확인해 주세요.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "translated": "예상치 못한 오류가 발생했습니다.",
            }

    def _grade_code(
        self,
        code: str,
        problem: dict,
        hints_used: int,
    ) -> dict:
        """제출된 코드를 채점하고 결과를 반환한다.

        core/grader.py의 grade_solution 함수를 사용한다.
        힌트 사용 횟수에 따라 보너스 점수를 계산한다.

        보너스 계산:
            - 힌트 0개 사용: +20% 보너스
            - 힌트 1개 사용: +13% 보너스
            - 힌트 2개 사용: +6% 보너스
            - 힌트 3개 사용: 보너스 없음

        Args:
            code: 채점할 Python 코드 문자열
            problem: 문제 딕셔너리 (test_cases 포함)
            hints_used: 사용한 힌트 수 (0 ~ 3)

        Returns:
            dict: 채점 결과
                {'passed': bool, 'score': float, 'passed_cases': int,
                 'total_cases': int, 'feedback': str,
                 'details': list[dict], 'bonus': float}
        """
        try:
            from core.grader import grade_solution  # type: ignore

            result = grade_solution(code, problem)

            # 힌트 미사용 보너스 계산 (0 ~ 0.2)
            # 힌트 1개당 7% 차감: 0→20%, 1→13%, 2→6%, 3→0%
            bonus = max(0.0, 0.20 - hints_used * 0.07)
            result["bonus"] = bonus

            return result

        except ImportError:
            # grader 미구현 시 기본 통과 결과 반환 (개발 편의)
            return {
                "passed": True,
                "score": 1.0,
                "passed_cases": 1,
                "total_cases": 1,
                "feedback": "채점 엔진(core/grader.py)을 찾을 수 없습니다. 임시 통과 처리됩니다.",
                "details": [],
                "bonus": max(0.0, 0.20 - hints_used * 0.07),
            }

    def _update_progress(self, prob_id: str, grade_result: dict) -> None:
        """문제 완료 후 진행도를 업데이트한다.

        progress_manager가 있으면 영구 저장, 없으면 session_state에만 기록한다.

        Args:
            prob_id: 완료된 문제의 ID
            grade_result: 채점 결과 딕셔너리
        """
        if self.progress_manager:
            try:
                self.progress_manager.mark_problem_done(
                    chapter_id=self.chapter_id,
                    problem_id=prob_id,
                    score=grade_result.get("score", 1.0),
                    bonus=grade_result.get("bonus", 0.0),
                )
            except Exception:
                pass  # 저장 실패는 UI 흐름 방해 안 함

        # session_state에도 기록 (progress_manager 없이도 탭 내 상태 유지)
        completed_key = f"completed_problems_{self.chapter_id}"
        if completed_key not in st.session_state:
            st.session_state[completed_key] = set()
        st.session_state[completed_key].add(prob_id)

    def _get_progress_dict(self) -> dict:
        """현재 진행도를 딕셔너리로 반환한다.

        render_problem_navigation에 전달할 형식으로 변환한다.

        Returns:
            dict: {'completed_problems': list[str]}
        """
        completed = set()

        if self.progress_manager:
            try:
                completed = set(
                    self.progress_manager.get_completed_problems(self.chapter_id)
                )
            except Exception:
                pass

        # session_state의 임시 완료 목록과 병합
        session_completed = st.session_state.get(
            f"completed_problems_{self.chapter_id}", set()
        )
        completed |= session_completed

        return {"completed_problems": list(completed)}
