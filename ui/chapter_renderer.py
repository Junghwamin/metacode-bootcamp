"""챕터 학습 페이지 렌더러.

챕터 데이터(JSON)를 읽어 개념 설명, 코드 예제, 문제 풀기, 퀴즈 탭으로
구성된 완전한 학습 페이지를 렌더링한다.
"""

import json
from pathlib import Path

import streamlit as st

from core.progress import ProgressManager
from ui.components import (
    render_difficulty_badge,
    render_grade_result,
    render_hint_panel,
    render_progress_bar,
)


# 데이터 경로 설정
_DATA_DIR = Path(__file__).parent.parent / "data"

# What/Why/How 섹션 스타일 정의
_WWH_STYLES = {
    "what": {
        "icon": "🔍",
        "label": "What - 이게 뭔가요?",
        "bg": "rgba(74, 144, 217, 0.06)",
        "border": "#4A90D9",
        "color": "#2B6CB0",
    },
    "why": {
        "icon": "💡",
        "label": "Why - 왜 필요한가요?",
        "bg": "rgba(255, 185, 70, 0.08)",
        "border": "#FFB946",
        "color": "#B8860B",
    },
    "how": {
        "icon": "🛠",
        "label": "How - 어떻게 쓰나요?",
        "bg": "rgba(0, 196, 140, 0.06)",
        "border": "#00C48C",
        "color": "#00865A",
    },
}


def _render_wwh_content(content: str) -> None:
    """What/Why/How 헤더가 있으면 색상 카드로 구분하여 렌더링한다.

    content_md에 '## What', '## Why', '## How' 패턴이 있으면
    각각 파란색/노란색/초록색 카드로 감싸서 표시한다.
    패턴이 없으면 일반 마크다운으로 렌더링한다.

    Args:
        content: 섹션의 content_md 문자열
    """
    import re

    # What/Why/How 패턴이 있는지 확인
    pattern = r'##\s*(What|Why|How)\s*[-–—:]?\s*'
    if not re.search(pattern, content, re.IGNORECASE):
        # 패턴 없으면 일반 마크다운
        st.markdown(content)
        return

    # What/Why/How 섹션으로 분할
    parts = re.split(r'(##\s*(?:What|Why|How)\s*[-–—:]?\s*)', content, flags=re.IGNORECASE)

    for i, part in enumerate(parts):
        match = re.match(r'##\s*(What|Why|How)\s*[-–—:]?\s*', part, re.IGNORECASE)
        if match:
            # 헤더 부분 - 다음 파트가 본문
            key = match.group(1).lower()
            style = _WWH_STYLES.get(key, _WWH_STYLES["what"])

            # 본문은 다음 파트
            if i + 1 < len(parts):
                body = parts[i + 1]
                parts[i + 1] = ""  # 중복 렌더링 방지

                st.markdown(
                    f'<div style="background:{style["bg"]};'
                    f'border-left:4px solid {style["border"]};'
                    f'border-radius:0 12px 12px 0;'
                    f'padding:14px 18px;margin:10px 0;">'
                    f'<div style="font-weight:700;color:{style["color"]};'
                    f'margin-bottom:8px;font-size:1.05em;">'
                    f'{style["icon"]} {style["label"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(body)
        elif part.strip():
            st.markdown(part)


def _load_json(path: Path) -> dict | list | None:
    """JSON 파일을 로드한다.

    Args:
        path: JSON 파일 경로

    Returns:
        dict | list | None: 파싱된 데이터 또는 실패 시 None
    """
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


class ChapterRenderer:
    """챕터 학습 페이지 렌더러.

    chapter_id에 해당하는 JSON 데이터를 로드하여
    개념/문제/퀴즈 탭으로 구성된 학습 페이지를 렌더링한다.

    Args:
        chapter_id: 렌더링할 챕터 번호 (1~8)

    Example:
        >>> renderer = ChapterRenderer(chapter_id=5)
        >>> renderer.render()
    """

    def __init__(self, chapter_id: int):
        """ChapterRenderer를 초기화하고 데이터를 로드한다.

        Args:
            chapter_id: 챕터 번호
        """
        self.chapter_id = chapter_id
        self.progress = ProgressManager()

        # JSON 데이터 로드
        self.chapter_data = _load_json(
            _DATA_DIR / "chapters" / f"chapter{chapter_id}.json"
        )
        self.problems_data = _load_json(
            _DATA_DIR / "problems" / f"chapter{chapter_id}_problems.json"
        )
        self.quiz_data = _load_json(
            _DATA_DIR / "quizzes" / f"chapter{chapter_id}_quiz.json"
        )

    def render(self) -> None:
        """챕터 전체 페이지를 렌더링한다.

        데이터 로드 실패 시 오류 메시지를 표시한다.
        성공 시 개념/문제/퀴즈 탭을 렌더링한다.
        """
        if not self.chapter_data:
            st.error(f"챕터 {self.chapter_id} 데이터를 불러올 수 없습니다.")
            return

        # 챕터 헤더
        st.title(f"챕터 {self.chapter_id}: {self.chapter_data.get('title', '')}")
        st.markdown(self.chapter_data.get("description", ""))

        # 진행도 표시
        completion = self.progress.get_chapter_completion(self.chapter_id)
        render_progress_bar(completion, f"챕터 {self.chapter_id} 진행도")

        st.divider()

        # 탭 구성
        tab1, tab2, tab3 = st.tabs(["📚 개념 학습", "💻 문제 풀기", "✅ 퀴즈"])

        with tab1:
            self._render_concept_tab()

        with tab2:
            self._render_problems_tab()

        with tab3:
            self._render_quiz_tab()

    def _render_concept_tab(self) -> None:
        """개념 학습 탭을 렌더링한다.

        학습 목표, 섹션별 개념 설명, 코드 예제, 핵심 포인트를 표시한다.
        """
        # 학습 목표
        objectives = self.chapter_data.get("learning_objectives", [])
        if objectives:
            with st.expander("학습 목표", expanded=True):
                for obj in objectives:
                    st.markdown(f"- {obj}")

        # 섹션별 렌더링
        sections = self.chapter_data.get("sections", [])
        for section in sections:
            st.subheader(f"{section.get('section_id', '').upper()} - {section.get('title', '')}")

            # 마크다운 내용 (What/Why/How 시각적 구분)
            content = section.get("content_md", "")
            if content:
                _render_wwh_content(content)

            # 코드 예제
            examples = section.get("code_examples", [])
            for example in examples:
                with st.expander(f"예제: {example.get('title', '')}", expanded=False):
                    st.code(example.get("code", ""), language="python")
                    if example.get("expected_output"):
                        st.caption("실행 결과:")
                        st.code(example.get("expected_output", ""), language="text")
                    if example.get("explanation"):
                        st.info(example.get("explanation", ""))

            # 핵심 포인트
            key_points = section.get("key_points", [])
            if key_points:
                st.markdown("**핵심 포인트**")
                for point in key_points:
                    st.markdown(
                        f'<div style="background:#EBF8FF;border-radius:6px;padding:6px 12px;'
                        f'margin:4px 0;font-size:0.9em;color:#2B6CB0;">✓ {point}</div>',
                        unsafe_allow_html=True,
                    )

            st.divider()

    def _render_problems_tab(self) -> None:
        """문제 풀기 탭을 렌더링한다.

        사이드바에 문제 목록을, 메인 영역에 선택된 문제를 표시한다.
        """
        if not self.problems_data:
            st.warning("문제 데이터를 불러올 수 없습니다.")
            return

        problems = self.problems_data.get("problems", [])
        if not problems:
            st.info("이 챕터에는 문제가 없습니다.")
            return

        # 문제 선택 상태 초기화
        state_key = f"ch{self.chapter_id}_problem_idx"
        if state_key not in st.session_state:
            st.session_state[state_key] = 0

        # 사이드바에 문제 목록 표시
        with st.sidebar:
            st.markdown(f"### 챕터 {self.chapter_id} 문제 목록")

            for i, problem in enumerate(problems):
                pid = problem.get("problem_id", "")
                status = self.progress.get_problem_status(pid)
                icon = "✅" if status.get("solved") else "○"
                difficulty = problem.get("difficulty", "basic")
                diff_labels = {"basic": "기초", "intermediate": "중급", "advanced": "심화"}
                diff_label = diff_labels.get(difficulty, "")

                if st.button(
                    f"{icon} {i+1}. {problem.get('title', '')} [{diff_label}]",
                    key=f"problem_nav_{self.chapter_id}_{i}",
                    use_container_width=True,
                ):
                    st.session_state[state_key] = i
                    st.rerun()

        # 선택된 문제 렌더링
        idx = st.session_state[state_key]
        if 0 <= idx < len(problems):
            self._render_single_problem(problems[idx], idx, len(problems))

    def _render_single_problem(
        self, problem: dict, idx: int, total: int
    ) -> None:
        """단일 문제를 렌더링한다.

        문제 설명, 코드 에디터, 힌트 시스템, 채점 결과를 표시한다.

        Args:
            problem: 문제 딕셔너리
            idx: 현재 문제 인덱스 (0-based)
            total: 전체 문제 수
        """
        pid = problem.get("problem_id", "")
        state_key = f"ch{self.chapter_id}_problem_idx"

        # 네비게이션
        col_prev, col_info, col_next = st.columns([1, 3, 1])
        with col_prev:
            if idx > 0 and st.button("이전", key=f"prev_{pid}"):
                st.session_state[state_key] = idx - 1
                st.rerun()
        with col_info:
            st.caption(f"문제 {idx + 1} / {total}")
        with col_next:
            if idx < total - 1 and st.button("다음", key=f"next_{pid}"):
                st.session_state[state_key] = idx + 1
                st.rerun()

        # 문제 헤더
        difficulty = problem.get("difficulty", "basic")
        st.markdown(
            f"### {problem.get('title', '')} "
            f"{render_difficulty_badge(difficulty)}",
            unsafe_allow_html=True,
        )

        st.markdown(problem.get("description", ""))

        # 지시사항
        instructions = problem.get("instructions", [])
        if instructions:
            st.markdown("**해야 할 일:**")
            for instr in instructions:
                st.markdown(f"- {instr}")

        # 풀이 상태 표시
        status = self.progress.get_problem_status(pid)
        if status.get("solved"):
            st.success(f"이미 풀었습니다! (점수: {int(status.get('score', 0) * 100)}점)")

        # 코드 에디터
        code_key = f"code_{pid}"
        if code_key not in st.session_state:
            st.session_state[code_key] = problem.get("initial_code", "")

        st.markdown("**코드 작성:**")
        user_code = st.text_area(
            "코드",
            value=st.session_state[code_key],
            height=250,
            key=f"editor_{pid}",
            label_visibility="collapsed",
        )
        st.session_state[code_key] = user_code

        # 힌트 시스템
        hints = problem.get("hints", [])
        hint_key = f"hints_used_{pid}"
        if hint_key not in st.session_state:
            st.session_state[hint_key] = 0

        hints_used = st.session_state[hint_key]

        col_hint, col_reset, col_submit = st.columns([1, 1, 2])
        with col_hint:
            if hints_used < len(hints):
                if st.button(
                    f"💡 힌트 보기 ({len(hints) - hints_used}개 남음)",
                    key=f"hint_{pid}",
                ):
                    st.session_state[hint_key] += 1
                    hints_used += 1

        with col_reset:
            if st.button("초기화", key=f"reset_{pid}"):
                st.session_state[code_key] = problem.get("initial_code", "")
                st.rerun()

        with col_submit:
            submit_clicked = st.button(
                "제출하기",
                key=f"submit_{pid}",
                type="primary",
                use_container_width=True,
            )

        # 힌트 표시
        for level in range(1, hints_used + 1):
            if level <= len(hints):
                hint_item = hints[level - 1]
                render_hint_panel(hint_item.get("text", ""), level)

        # 채점
        if submit_clicked:
            self._grade_and_show(problem, user_code, hints_used)

    def _grade_and_show(
        self, problem: dict, user_code: str, hints_used: int
    ) -> None:
        """코드를 채점하고 결과를 표시한다.

        채점 방식에 따라 결과를 계산하고 진행도를 업데이트한다.

        Args:
            problem: 문제 딕셔너리
            user_code: 사용자 코드 문자열
            hints_used: 사용한 힌트 수
        """
        # 동적 import로 순환 의존성 방지
        try:
            from core.executor import CodeExecutor
            from core.grader import Grader

            executor = CodeExecutor()
            grader = Grader(executor=executor)

            with st.spinner("채점 중..."):
                result = grader.grade(user_code, problem)

            # 힌트 점수 배율 적용
            score_multiplier = self._get_hint_multiplier(hints_used)
            final_score = min(1.0, result.score * score_multiplier)
            final_passed = result.passed and final_score >= 1.0

            render_grade_result(final_passed, final_score, result.feedback)

            # 진행도 기록
            self.progress.mark_problem_solved(
                problem.get("problem_id", ""),
                score=final_score,
                hints_used=hints_used,
            )

        except Exception as e:
            st.error(f"채점 중 오류가 발생했습니다: {e}")

    def _get_hint_multiplier(self, hints_used: int) -> float:
        """힌트 사용 수에 따른 점수 배율을 반환한다.

        Args:
            hints_used: 사용한 힌트 수

        Returns:
            float: 점수 배율 (0.7 ~ 1.2)
        """
        table = {0: 1.2, 1: 1.0, 2: 0.9, 3: 0.7}
        if hints_used <= 0:
            return table[0]
        return table.get(min(hints_used, 3), 0.7)

    def _render_quiz_tab(self) -> None:
        """퀴즈 탭을 렌더링한다.

        10개 퀴즈 문제를 순서대로 표시하고 채점 결과를 보여준다.
        """
        if not self.quiz_data:
            st.warning("퀴즈 데이터를 불러올 수 없습니다.")
            return

        st.subheader(self.quiz_data.get("quiz_title", f"챕터 {self.chapter_id} 퀴즈"))
        passing_score = self.quiz_data.get("passing_score", 0.6)
        questions = self.quiz_data.get("questions", [])

        if not questions:
            st.info("퀴즈 문제가 없습니다.")
            return

        st.info(f"총 {len(questions)}문제 · 합격 기준: {int(passing_score * 100)}점 이상")

        # 퀴즈 답변 상태
        quiz_state_key = f"quiz_answers_{self.chapter_id}"
        if quiz_state_key not in st.session_state:
            st.session_state[quiz_state_key] = {}

        answers = st.session_state[quiz_state_key]

        # 퀴즈 제출 상태
        quiz_submitted_key = f"quiz_submitted_{self.chapter_id}"

        with st.form(key=f"quiz_form_{self.chapter_id}"):
            for i, q in enumerate(questions, 1):
                qid = q.get("question_id", f"q{i}")
                q_type = q.get("type", "multiple_choice")
                question_text = q.get("question", "")

                st.markdown(f"**문제 {i}.** {question_text}")

                options = q.get("options", [])

                if q_type == "multiple_choice":
                    answer = st.radio(
                        f"선택 {i}",
                        options=options,
                        key=f"quiz_{self.chapter_id}_{qid}",
                        label_visibility="collapsed",
                    )
                    answers[qid] = answer

                elif q_type == "ox":
                    answer = st.radio(
                        f"O/X {i}",
                        options=["O", "X"],
                        key=f"quiz_{self.chapter_id}_{qid}",
                        label_visibility="collapsed",
                    )
                    answers[qid] = answer

                elif q_type == "fill_blank":
                    answer = st.text_input(
                        f"빈칸 {i}",
                        key=f"quiz_{self.chapter_id}_{qid}",
                        placeholder="답을 입력하세요",
                        label_visibility="collapsed",
                    )
                    answers[qid] = answer

                st.markdown("---")

            submitted = st.form_submit_button(
                "퀴즈 제출",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            st.session_state[quiz_submitted_key] = True
            self._grade_quiz(questions, answers, passing_score)
        elif st.session_state.get(quiz_submitted_key):
            self._grade_quiz(questions, answers, passing_score)

    def _grade_quiz(
        self, questions: list, answers: dict, passing_score: float
    ) -> None:
        """퀴즈를 채점하고 결과를 표시한다.

        Args:
            questions: 퀴즈 문제 리스트
            answers: 사용자 답변 딕셔너리
            passing_score: 합격 기준 점수 (0.0 ~ 1.0)
        """
        correct_count = 0
        total = len(questions)

        st.subheader("채점 결과")

        for i, q in enumerate(questions, 1):
            qid = q.get("question_id", "")
            correct = q.get("correct_answer", "")
            user_answer = answers.get(qid, "")
            explanation = q.get("explanation", "")

            # 대소문자 무시 비교
            is_correct = str(user_answer).strip().lower() == str(correct).strip().lower()

            if is_correct:
                correct_count += 1
                self.progress.mark_quiz_answered(qid, True)
                st.success(f"문제 {i}: ✅ 정답 ({correct})")
            else:
                self.progress.mark_quiz_answered(qid, False)
                st.error(
                    f"문제 {i}: ❌ 오답 (내 답: {user_answer} / 정답: {correct})"
                )

            if explanation:
                st.caption(f"해설: {explanation}")

        # 최종 점수
        score = correct_count / total if total > 0 else 0.0
        pct = int(score * 100)

        st.divider()
        if score >= passing_score:
            st.balloons()
            st.success(
                f"합격! {total}문제 중 {correct_count}개 정답 ({pct}점) - "
                f"합격 기준 {int(passing_score * 100)}점 달성!"
            )
        else:
            st.warning(
                f"아쉬워요! {total}문제 중 {correct_count}개 정답 ({pct}점) - "
                f"합격 기준: {int(passing_score * 100)}점"
            )
