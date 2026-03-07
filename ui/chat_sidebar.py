"""사이드바 AI 튜터 채팅 모듈.

모든 학습 페이지에서 호출하여 사이드바에 접이식 AI 튜터를 제공한다.
현재 챕터/문제 컨텍스트를 자동 감지하여 맞춤형 답변을 생성한다.
"""

import streamlit as st


def render_chat_sidebar(chapter_id: int = None, problem_title: str = None) -> None:
    """사이드바에 AI 튜터 채팅을 렌더링한다.

    토글 버튼으로 열고 닫을 수 있으며, 현재 학습 중인 챕터와
    문제 컨텍스트를 자동으로 GPT에 전달한다.

    Args:
        chapter_id: 현재 챕터 번호 (1~8, None이면 일반 모드)
        problem_title: 현재 문제 제목 (선택)
    """
    # API 키 확인
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return

    with st.sidebar:
        st.markdown("---")

        # 토글 상태 관리
        if "chat_open" not in st.session_state:
            st.session_state["chat_open"] = False
        if "sidebar_messages" not in st.session_state:
            st.session_state["sidebar_messages"] = []
        if "chat_count" not in st.session_state:
            st.session_state["chat_count"] = 0

        # 헤더 + 토글 버튼
        col_title, col_toggle = st.columns([3, 1])
        with col_title:
            st.markdown(
                '<p style="font-weight:700;font-size:0.95em;margin:0;'
                'color:#6C63FF;">AI 튜터</p>',
                unsafe_allow_html=True,
            )
        with col_toggle:
            icon = "▼" if st.session_state["chat_open"] else "▶"
            if st.button(icon, key="chat_toggle", use_container_width=True):
                st.session_state["chat_open"] = not st.session_state["chat_open"]
                st.rerun()

        if not st.session_state["chat_open"]:
            st.caption("궁금한 점이 있으면 열어보세요")
            return

        # 컨텍스트 표시
        if chapter_id:
            ctx_label = f"챕터 {chapter_id}"
            if problem_title:
                ctx_label += f" · {problem_title}"
            st.caption(f"학습 중: {ctx_label}")

        # 남은 횟수
        remaining = max(0, 30 - st.session_state["chat_count"])
        st.caption(f"남은 질문: {remaining}회")

        # 대화 기록 표시
        chat_container = st.container(height=300)
        with chat_container:
            if not st.session_state["sidebar_messages"]:
                st.markdown(
                    '<p style="color:#636E72;font-size:0.85em;text-align:center;'
                    'padding:20px 0;">질문을 입력해보세요!</p>',
                    unsafe_allow_html=True,
                )
            for msg in st.session_state["sidebar_messages"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"], unsafe_allow_html=False)

        # 빠른 질문 버튼
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            if st.button("개념 질문", key="sq_concept", use_container_width=True):
                _send_quick(api_key, "이 부분 개념이 이해가 안 돼요",
                            chapter_id, problem_title)
        with q_col2:
            if st.button("힌트 요청", key="sq_hint", use_container_width=True):
                _send_quick(api_key, "힌트를 주세요",
                            chapter_id, problem_title)

        # 입력창
        user_input = st.text_input(
            "질문 입력",
            key="sidebar_chat_input",
            placeholder="궁금한 점을 물어보세요...",
            label_visibility="collapsed",
        )

        col_send, col_clear = st.columns([3, 1])
        with col_send:
            if st.button("보내기", key="sidebar_send", use_container_width=True,
                         type="primary"):
                if user_input and user_input.strip():
                    _send_message(api_key, user_input.strip(),
                                  chapter_id, problem_title)
        with col_clear:
            if st.button("지우기", key="sidebar_clear", use_container_width=True):
                st.session_state["sidebar_messages"] = []
                st.rerun()


def _send_quick(api_key: str, question: str,
                chapter_id: int = None, problem_title: str = None) -> None:
    """빠른 질문을 전송한다."""
    _send_message(api_key, question, chapter_id, problem_title)


def _send_message(api_key: str, message: str,
                  chapter_id: int = None, problem_title: str = None) -> None:
    """메시지를 GPT에 전송하고 응답을 받는다.

    Args:
        api_key: OpenAI API 키
        message: 사용자 메시지
        chapter_id: 현재 챕터 번호
        problem_title: 현재 문제 제목
    """
    if st.session_state["chat_count"] >= 30:
        st.error("오늘의 질문 횟수를 모두 사용했습니다.")
        return

    from core.chatbot import chat_with_tutor

    st.session_state["sidebar_messages"].append(
        {"role": "user", "content": message}
    )

    try:
        reply = chat_with_tutor(
            st.session_state["sidebar_messages"],
            api_key,
            chapter_id=chapter_id,
            problem_title=problem_title,
        )
        st.session_state["sidebar_messages"].append(
            {"role": "assistant", "content": reply}
        )
        st.session_state["chat_count"] += 1
    except Exception as e:
        st.session_state["sidebar_messages"].append(
            {"role": "assistant",
             "content": f"오류가 발생했습니다: {str(e)[:100]}"}
        )

    st.rerun()
