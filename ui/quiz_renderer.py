"""퀴즈 렌더링 모듈.

객관식(multiple_choice), O/X(ox), 빈칸 채우기(fill_blank) 세 가지
문제 유형을 지원한다.

학습자 경험 설계:
    - 즉시 채점: 제출 즉시 결과 표시 (딜레이 없음)
    - 재응시 옵션: 이전 점수를 표시하며 재시도 가능
    - 부분 점수: 맞은 문제 수 기반으로 점수 표시
    - 정답 해설: 채점 후 각 문제의 정답과 해설 표시
"""

import streamlit as st


class QuizRenderer:
    """퀴즈 렌더러.

    챕터별 퀴즈를 렌더링하고 채점한다.
    이미 응시한 경우 점수를 표시하고 재응시 옵션을 제공한다.

    Attributes:
        chapter_id (int): 챕터 번호
        quiz_data (dict): 퀴즈 데이터
        progress_manager: 진행도 관리 객체 (optional)

    퀴즈 데이터 구조:
        {
            'title': str,           # 퀴즈 제목
            'description': str,     # 퀴즈 설명 (optional)
            'passing_score': float, # 합격 점수 (0.0~1.0), 기본 0.7
            'questions': [
                {
                    'id': str,
                    'type': 'multiple_choice' | 'ox' | 'fill_blank',
                    'question': str,          # 문제 텍스트
                    'options': list[str],     # 선택지 (multiple_choice만)
                    'correct_answer': str,    # 정답 (ox: 'O' | 'X')
                    'explanation': str,       # 해설 (optional)
                    'points': int,            # 배점, 기본 1
                }
            ]
        }

    session_state 키 규칙:
        - f"quiz_answers_{chapter_id}": dict - 문제ID → 사용자 답변
        - f"quiz_submitted_{chapter_id}": bool - 제출 여부
        - f"quiz_score_{chapter_id}": float - 최종 점수 (0.0~1.0)
        - f"quiz_retake_{chapter_id}": bool - 재응시 모드 여부
    """

    def __init__(
        self,
        chapter_id: int,
        quiz_data: dict,
        progress_manager=None,
    ) -> None:
        """QuizRenderer를 초기화한다.

        Args:
            chapter_id: 챕터 번호
            quiz_data: 퀴즈 데이터 딕셔너리
            progress_manager: 진행도 관리 객체. None이면 저장 생략.
        """
        self.chapter_id = chapter_id
        self.quiz_data = quiz_data or {}
        self.progress_manager = progress_manager

        self.questions: list = self.quiz_data.get("questions", [])
        self.passing_score: float = self.quiz_data.get("passing_score", 0.7)

        # session_state 초기화
        answers_key = f"quiz_answers_{chapter_id}"
        if answers_key not in st.session_state:
            st.session_state[answers_key] = {}

    def render(self) -> None:
        """전체 퀴즈 UI를 렌더링한다.

        이미 제출된 상태이면 결과를 표시하고 재응시 옵션을 제공한다.
        아직 제출 전이면 문제를 표시하고 제출 버튼을 렌더링한다.

        구조:
            1. 퀴즈 헤더 (제목, 문항 수, 합격 기준)
            2. 이미 응시한 경우: 점수 표시 + 재응시 버튼
            3. 미응시 또는 재응시 중: 문제 목록 + 제출 버튼
            4. 제출 후: 채점 결과 + 문제별 정답/해설
        """
        submitted_key = f"quiz_submitted_{self.chapter_id}"
        score_key = f"quiz_score_{self.chapter_id}"
        retake_key = f"quiz_retake_{self.chapter_id}"

        # ---- 1. 퀴즈 헤더 ----
        quiz_title = self.quiz_data.get("title", f"챕터 {self.chapter_id} 퀴즈")
        quiz_description = self.quiz_data.get("description", "")

        st.markdown(f"### {quiz_title}")
        if quiz_description:
            st.markdown(quiz_description)

        if self.questions:
            passing_pct = int(self.passing_score * 100)
            st.markdown(
                f"""
                <div style="background:#F7FAFC; border-radius:6px; padding:0.5rem 0.75rem;
                            font-size:0.88em; color:#4A5568; margin-bottom:1rem;">
                    📊 총 {len(self.questions)}문항 ·
                    합격 기준: {passing_pct}% 이상 ({int(self.passing_score * len(self.questions))}문항 이상 정답)
                </div>
                """,
                unsafe_allow_html=True,
            )

        if not self.questions:
            st.info("퀴즈 문항이 없습니다.")
            return

        # ---- 2. 이미 응시한 경우 (재응시 모드 아님) ----
        # 이전에 제출 완료 + 재응시 모드가 아닌 상태
        already_submitted = st.session_state.get(submitted_key, False)
        is_retake = st.session_state.get(retake_key, False)

        if already_submitted and not is_retake:
            # 이전 점수 표시
            previous_score = st.session_state.get(score_key, 0.0)
            self._render_score_summary(previous_score, show_retake_option=True)

            # 이전 답변과 정답/해설 표시
            st.markdown("---")
            st.markdown("**이전 응시 결과 상세:**")
            answers = st.session_state.get(f"quiz_answers_{self.chapter_id}", {})
            self._render_review(answers)
            return

        # ---- 3. 문제 목록 렌더링 ----
        # 재응시 시작: 이전 답변 초기화
        if is_retake:
            st.session_state[f"quiz_answers_{self.chapter_id}"] = {}
            st.session_state[submitted_key] = False
            st.session_state[retake_key] = False
            st.rerun()

        # 각 문제 렌더링
        for i, question in enumerate(self.questions):
            st.markdown(f"**Q{i+1}.**", )
            q_type = question.get("type", "multiple_choice")

            if q_type == "multiple_choice":
                self._render_multiple_choice(question, i)
            elif q_type == "ox":
                self._render_ox(question, i)
            elif q_type == "fill_blank":
                self._render_fill_blank(question, i)
            else:
                # 알 수 없는 타입: 기본 텍스트 입력
                st.warning(f"알 수 없는 문제 유형: {q_type}")

            st.markdown("<br>", unsafe_allow_html=True)

        # ---- 4. 제출 버튼 ----
        st.markdown("---")

        # 답변 완료 여부 확인
        answers = st.session_state.get(f"quiz_answers_{self.chapter_id}", {})
        answered_count = sum(
            1 for q in self.questions if q.get("id") in answers and answers[q.get("id")] is not None
        )
        unanswered = len(self.questions) - answered_count

        if unanswered > 0:
            st.warning(f"⚠️ {unanswered}개 문항에 아직 답하지 않았어요.")

        col_submit, _ = st.columns([1, 2])
        with col_submit:
            if st.button(
                "퀴즈 제출하기",
                key=f"quiz_submit_{self.chapter_id}",
                use_container_width=True,
                type="primary",
                disabled=(unanswered == len(self.questions)),  # 하나도 안 답하면 비활성화
            ):
                self._grade_quiz()
                st.rerun()

    def _render_multiple_choice(self, question: dict, q_index: int) -> None:
        """객관식 문제를 radio 버튼으로 렌더링한다.

        선택 결과는 session_state["quiz_answers_{chapter_id}"]에 저장된다.

        Args:
            question: 문제 딕셔너리.
                필요 키: {'id': str, 'question': str, 'options': list[str]}
            q_index: 문제 인덱스 (0부터 시작, 위젯 키 구분용)
        """
        q_id = question.get("id", f"q_{q_index}")
        q_text = question.get("question", "")
        options = question.get("options", [])

        st.markdown(q_text)

        if not options:
            st.warning("선택지가 없습니다.")
            return

        # 현재 저장된 답변 불러오기
        answers_key = f"quiz_answers_{self.chapter_id}"
        current_answer = st.session_state.get(answers_key, {}).get(q_id)

        # 현재 답변의 인덱스 (없으면 None → index=None으로 미선택 상태)
        current_idx = None
        if current_answer in options:
            current_idx = options.index(current_answer)

        # radio 버튼 렌더링
        selected = st.radio(
            label=f"문제 {q_index+1} 선택",
            options=options,
            index=current_idx,
            key=f"mc_{self.chapter_id}_{q_id}",
            label_visibility="collapsed",
        )

        # 선택 결과 저장
        if selected is not None:
            if answers_key not in st.session_state:
                st.session_state[answers_key] = {}
            st.session_state[answers_key][q_id] = selected

    def _render_ox(self, question: dict, q_index: int) -> None:
        """O/X 문제를 radio 버튼으로 렌더링한다.

        O와 X 두 가지 선택지만 표시한다.
        선택 결과는 "O" 또는 "X" 문자열로 저장된다.

        Args:
            question: 문제 딕셔너리.
                필요 키: {'id': str, 'question': str}
            q_index: 문제 인덱스 (0부터 시작)
        """
        q_id = question.get("id", f"q_{q_index}")
        q_text = question.get("question", "")

        st.markdown(q_text)

        answers_key = f"quiz_answers_{self.chapter_id}"
        current_answer = st.session_state.get(answers_key, {}).get(q_id)

        # O/X 선택지 (대형 아이콘으로 표시)
        ox_options = ["O (맞다)", "X (틀리다)"]
        ox_values = {"O (맞다)": "O", "X (틀리다)": "X"}

        # 현재 답변에 해당하는 레이블 찾기
        current_label = None
        for label, val in ox_values.items():
            if val == current_answer:
                current_label = label
                break

        current_idx = ox_options.index(current_label) if current_label in ox_options else None

        selected = st.radio(
            label=f"문제 {q_index+1} O/X",
            options=ox_options,
            index=current_idx,
            key=f"ox_{self.chapter_id}_{q_id}",
            horizontal=True,
            label_visibility="collapsed",
        )

        # "O (맞다)" → "O", "X (틀리다)" → "X" 변환하여 저장
        if selected is not None:
            if answers_key not in st.session_state:
                st.session_state[answers_key] = {}
            st.session_state[answers_key][q_id] = ox_values.get(selected, selected)

    def _render_fill_blank(self, question: dict, q_index: int) -> None:
        """빈칸 채우기 문제를 text_input으로 렌더링한다.

        대소문자 구분 없이 채점할 수 있도록 입력값을 정규화한다.
        (채점 시 .strip().lower() 적용)

        Args:
            question: 문제 딕셔너리.
                필요 키: {'id': str, 'question': str}
                선택 키: {'placeholder': str}  # 입력창 힌트 텍스트
            q_index: 문제 인덱스 (0부터 시작)
        """
        q_id = question.get("id", f"q_{q_index}")
        q_text = question.get("question", "")
        placeholder = question.get("placeholder", "답을 입력하세요...")

        st.markdown(q_text)

        answers_key = f"quiz_answers_{self.chapter_id}"
        current_answer = st.session_state.get(answers_key, {}).get(q_id, "")

        user_input = st.text_input(
            label=f"문제 {q_index+1} 답변",
            value=current_answer,
            placeholder=placeholder,
            key=f"fill_{self.chapter_id}_{q_id}",
            label_visibility="collapsed",
        )

        # 입력값 저장 (빈 문자열도 저장하여 "미답"과 "빈 답" 구분)
        if answers_key not in st.session_state:
            st.session_state[answers_key] = {}
        st.session_state[answers_key][q_id] = user_input

    def _grade_quiz(self) -> None:
        """전체 퀴즈를 채점하고 결과를 session_state에 저장한다.

        채점 로직:
            - multiple_choice: 정확히 일치 (대소문자 구분)
            - ox: 정확히 일치 ("O" 또는 "X")
            - fill_blank: strip().lower() 후 비교 (대소문자 무시)

        점수 계산:
            배점(points) 기반 가중 평균.
            points 키 없으면 모든 문제 동등 배점(1점).

        채점 완료 후 session_state 업데이트:
            - quiz_submitted_{chapter_id} = True
            - quiz_score_{chapter_id} = float (0.0~1.0)
            - quiz_grade_details_{chapter_id} = list[dict]

        진행도 업데이트:
            합격 점수(passing_score) 이상이면 progress_manager에 완료 기록.
        """
        submitted_key = f"quiz_submitted_{self.chapter_id}"
        score_key = f"quiz_score_{self.chapter_id}"
        details_key = f"quiz_grade_details_{self.chapter_id}"
        answers_key = f"quiz_answers_{self.chapter_id}"

        answers = st.session_state.get(answers_key, {})

        # 채점 상세 결과 계산
        details = []
        total_points = 0
        earned_points = 0

        for question in self.questions:
            q_id = question.get("id", "")
            q_type = question.get("type", "multiple_choice")
            correct_answer = question.get("correct_answer", "")
            user_answer = answers.get(q_id, "")
            points = question.get("points", 1)
            explanation = question.get("explanation", "")

            # 타입별 정답 비교
            is_correct = False
            if q_type in ("multiple_choice", "ox"):
                # 정확히 일치 비교
                is_correct = str(user_answer).strip() == str(correct_answer).strip()
            elif q_type == "fill_blank":
                # 대소문자 무시 + 앞뒤 공백 제거
                is_correct = (
                    str(user_answer).strip().lower()
                    == str(correct_answer).strip().lower()
                )

            # 점수 누적
            total_points += points
            if is_correct:
                earned_points += points

            details.append({
                "q_id": q_id,
                "q_type": q_type,
                "question": question.get("question", ""),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "points": points,
                "explanation": explanation,
            })

        # 최종 점수 계산 (0으로 나누기 방지)
        final_score = earned_points / total_points if total_points > 0 else 0.0

        # session_state 업데이트
        st.session_state[submitted_key] = True
        st.session_state[score_key] = final_score
        st.session_state[details_key] = details

        # 진행도 업데이트 (합격 시)
        if final_score >= self.passing_score and self.progress_manager:
            try:
                self.progress_manager.mark_quiz_done(
                    chapter_id=self.chapter_id,
                    score=final_score,
                )
            except Exception:
                pass  # 저장 실패는 UI 흐름 방해 안 함

        # session_state 기록 (progress_manager 없을 때 탭 상태 유지)
        st.session_state[f"quiz_done_{self.chapter_id}"] = (
            final_score >= self.passing_score
        )

    def _render_score_summary(
        self, score: float, show_retake_option: bool = False
    ) -> None:
        """퀴즈 점수 요약을 렌더링한다.

        합격/불합격에 따라 다른 디자인으로 표시한다.

        Args:
            score: 점수 (0.0 ~ 1.0)
            show_retake_option: True이면 재응시 버튼 표시
        """
        score_pct = int(score * 100)
        passing_pct = int(self.passing_score * 100)
        passed = score >= self.passing_score

        if passed:
            st.markdown(
                f"""
                <div style="background:#F0FFF4; border:2px solid #48BB78;
                            border-radius:10px; padding:1.5rem; text-align:center;
                            margin:0.75rem 0;">
                    <div style="font-size:2.5rem; margin-bottom:0.5rem;">🎉</div>
                    <div style="font-weight:700; color:#276749; font-size:1.2em;">
                        퀴즈 합격!
                    </div>
                    <div style="color:#2F855A; font-size:1.1em; margin-top:0.4rem;">
                        점수: <strong>{score_pct}점</strong> / 합격 기준: {passing_pct}점
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style="background:#FFF5F5; border:2px solid #F56565;
                            border-radius:10px; padding:1.5rem; text-align:center;
                            margin:0.75rem 0;">
                    <div style="font-size:2.5rem; margin-bottom:0.5rem;">📚</div>
                    <div style="font-weight:700; color:#C53030; font-size:1.2em;">
                        아직 합격 기준에 미달이에요
                    </div>
                    <div style="color:#742A2A; font-size:1.0em; margin-top:0.4rem;">
                        점수: <strong>{score_pct}점</strong> / 합격 기준: {passing_pct}점
                    </div>
                    <div style="color:#742A2A; font-size:0.88em; margin-top:0.5rem;">
                        개념 탭을 다시 살펴보고 재응시해 보세요!
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 재응시 버튼
        if show_retake_option:
            col_retake, _ = st.columns([1, 2])
            with col_retake:
                if st.button(
                    "다시 응시하기",
                    key=f"quiz_retake_{self.chapter_id}_btn",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state[f"quiz_retake_{self.chapter_id}"] = True
                    st.rerun()

    def _render_review(self, answers: dict) -> None:
        """채점 완료 후 문제별 정답/해설을 렌더링한다.

        맞은 문제는 초록색, 틀린 문제는 빨간색으로 표시한다.
        각 문제의 내 답변, 정답, 해설을 함께 보여준다.

        Args:
            answers: 사용자 답변 딕셔너리 {문제ID: 답변}
        """
        details_key = f"quiz_grade_details_{self.chapter_id}"
        details = st.session_state.get(details_key, [])

        if not details:
            # 채점 상세 없으면 기본 답변만 표시
            for i, question in enumerate(self.questions):
                q_id = question.get("id", f"q_{i}")
                user_answer = answers.get(q_id, "(미응답)")
                correct = question.get("correct_answer", "")
                is_correct = str(user_answer).strip() == str(correct).strip()

                icon = "✅" if is_correct else "❌"
                st.markdown(f"{icon} **Q{i+1}.** {question.get('question', '')}")
            return

        # 상세 채점 결과 렌더링
        for i, detail in enumerate(details):
            is_correct = detail.get("is_correct", False)
            icon = "✅" if is_correct else "❌"
            question_text = detail.get("question", "")
            user_answer = detail.get("user_answer", "(미응답)")
            correct_answer = detail.get("correct_answer", "")
            explanation = detail.get("explanation", "")

            # 정답/오답 색상 구분
            border_color = "#48BB78" if is_correct else "#F56565"
            bg_color = "#F0FFF4" if is_correct else "#FFF5F5"
            text_color = "#276749" if is_correct else "#742A2A"

            st.markdown(
                f"""
                <div style="background:{bg_color}; border-left:3px solid {border_color};
                            border-radius:0 8px 8px 0; padding:0.75rem 1rem;
                            margin:0.5rem 0;">
                    <div style="font-weight:700; color:{text_color}; margin-bottom:0.4rem;">
                        {icon} Q{i+1}. {question_text}
                    </div>
                    <div style="font-size:0.88em; color:#4A5568;">
                        내 답변: <strong>{user_answer}</strong>
                    </div>
                    <div style="font-size:0.88em; color:#4A5568;">
                        정답: <strong>{correct_answer}</strong>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            # 해설이 있는 경우 표시
            if explanation:
                st.markdown(
                    f"""
                    <div style="font-size:0.85em; color:#718096; margin-top:0.4rem;
                                padding-top:0.4rem; border-top:1px solid #E2E8F0;">
                        💡 <em>{explanation}</em>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)
