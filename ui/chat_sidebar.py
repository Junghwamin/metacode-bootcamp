"""오른쪽 패널 AI 튜터 채팅 모듈.

모든 학습 페이지에서 호출하여 화면 오른쪽에 접이식 AI 튜터를 제공한다.
현재 챕터/문제 컨텍스트를 자동 감지하여 맞춤형 답변을 생성한다.

사용법:
    content_col = render_chat_panel(chapter_id=1)
    with content_col:
        # 메인 콘텐츠 렌더링
        renderer.render()
"""

import streamlit as st


def render_chat_panel(chapter_id: int = None, problem_title: str = None):
    """오른쪽 채팅 패널 레이아웃을 설정하고 콘텐츠 컬럼을 반환한다.

    Args:
        chapter_id: 현재 챕터 번호 (1~8, None이면 일반 모드)
        problem_title: 현재 문제 제목 (선택)

    Returns:
        content_col: 메인 콘텐츠를 렌더링할 컬럼 (with 문으로 사용)
    """
    # API 키 확인
    api_key = st.secrets.get("OPENAI_API_KEY", "")

    # 세션 상태 초기화
    if "chat_open" not in st.session_state:
        st.session_state["chat_open"] = False
    if "sidebar_messages" not in st.session_state:
        st.session_state["sidebar_messages"] = []
    if "chat_count" not in st.session_state:
        st.session_state["chat_count"] = 0

    # API 키 없으면 채팅 비활성화 -> 전체 너비 컨텐츠
    if not api_key:
        return st.container()

    # 쿼리 파라미터로 채팅 열기 감지
    qp = st.query_params
    if qp.get("chat") == "open":
        st.session_state["chat_open"] = True
        st.query_params.clear()
    elif qp.get("chat") == "close":
        st.session_state["chat_open"] = False
        st.query_params.clear()

    # 채팅 열림/닫힘에 따라 레이아웃 분기
    if st.session_state["chat_open"]:
        # 채팅 패널 오른쪽 컬럼 스타일 주입
        _inject_chat_panel_css()
        content_col, chat_col = st.columns([4, 1.5], gap="small")
        with chat_col:
            _render_chat_content(api_key, chapter_id, problem_title)
        return content_col
    else:
        _render_floating_button()
        return st.container()


def _inject_chat_panel_css():
    """채팅 패널이 열려 있을 때만 오른쪽 컬럼에 스타일을 적용한다.

    첫 번째(최상위) stHorizontalBlock의 마지막 컬럼만 타겟한다.
    채팅이 닫히면 이 CSS가 렌더링되지 않으므로 다른 컬럼에 영향 없음.
    """
    st.markdown(
        """
        <style>
        /* 최상위 컬럼 블록의 마지막 컬럼 = 채팅 패널 */
        .main .block-container > div > div > div[data-testid="stHorizontalBlock"]
        > div[data-testid="stColumn"]:last-child {
            background: linear-gradient(180deg, #F8F9FE 0%, #F0F2FF 100%);
            border-left: 2px solid #E2E8F0;
            border-radius: 16px 0 0 16px;
            padding: 16px 12px !important;
            position: sticky;
            top: 56px;
            height: calc(100vh - 72px);
            overflow-y: auto;
        }

        /* 채팅 패널 내 스크롤바 */
        .main .block-container > div > div > div[data-testid="stHorizontalBlock"]
        > div[data-testid="stColumn"]:last-child::-webkit-scrollbar {
            width: 4px;
        }
        .main .block-container > div > div > div[data-testid="stHorizontalBlock"]
        > div[data-testid="stColumn"]:last-child::-webkit-scrollbar-thumb {
            background: rgba(108, 99, 255, 0.2);
            border-radius: 2px;
        }

        /* 채팅 열림 시 max-width 해제 */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_floating_button():
    """오른쪽 하단 플로팅 채팅 버튼을 렌더링한다."""
    st.markdown(
        """
        <div style="
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 999;
        ">
            <a href="?chat=open" target="_self" style="
                display: flex;
                align-items: center;
                gap: 8px;
                background: linear-gradient(135deg, #6C63FF, #4A90D9);
                color: white;
                text-decoration: none;
                border-radius: 28px;
                padding: 12px 20px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Noto Sans KR', 'Inter', sans-serif;
                box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4);
                transition: all 0.2s ease;
                user-select: none;
            "
            onmouseover="this.style.transform='scale(1.05)';this.style.boxShadow='0 6px 20px rgba(108,99,255,0.6)';"
            onmouseout="this.style.transform='scale(1)';this.style.boxShadow='0 4px 15px rgba(108,99,255,0.4)';"
            >
                <span style="font-size:20px;">💬</span>
                AI 튜터
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_chat_content(api_key: str, chapter_id: int = None,
                         problem_title: str = None):
    """채팅 패널 내부 UI를 렌더링한다.

    Args:
        api_key: OpenAI API 키
        chapter_id: 현재 챕터 번호
        problem_title: 현재 문제 제목
    """
    # 헤더
    col_title, col_close = st.columns([5, 1])
    with col_title:
        st.markdown(
            '<p style="font-weight:700;font-size:1.1em;margin:0 0 4px 0;'
            'color:#6C63FF;">💬 AI 튜터</p>',
            unsafe_allow_html=True,
        )
    with col_close:
        if st.button("✕", key="chat_close", help="닫기"):
            st.session_state["chat_open"] = False
            st.rerun()

    # 컨텍스트 + 남은 횟수
    remaining = max(0, 30 - st.session_state["chat_count"])
    info_parts = []
    if chapter_id:
        info_parts.append(f"챕터 {chapter_id}")
        if problem_title:
            info_parts[-1] += f" · {problem_title}"
    info_parts.append(f"남은 질문 {remaining}회")
    st.caption(" | ".join(info_parts))

    st.divider()

    # 대화 기록
    chat_container = st.container(height=320)
    with chat_container:
        if not st.session_state["sidebar_messages"]:
            st.markdown(
                '<div style="text-align:center;padding:60px 8px;color:#9CA3AF;">'
                '<div style="font-size:2em;margin-bottom:8px;">🤖</div>'
                '<div style="font-size:0.88em;line-height:1.6;">'
                'Python 학습 중 궁금한 점을<br>물어보세요!</div></div>',
                unsafe_allow_html=True,
            )
        for msg in st.session_state["sidebar_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=False)

    # 빠른 질문
    q1, q2 = st.columns(2)
    with q1:
        if st.button("💡 개념 질문", key="sq_concept", use_container_width=True):
            _send_message(api_key, "이 부분 개념이 이해가 안 돼요",
                          chapter_id, problem_title)
    with q2:
        if st.button("🔍 힌트 요청", key="sq_hint", use_container_width=True):
            _send_message(api_key, "힌트를 주세요",
                          chapter_id, problem_title)

    # 입력
    user_input = st.chat_input(
        "질문을 입력하세요...",
        key="chat_input_right",
    )
    if user_input and user_input.strip():
        _send_message(api_key, user_input.strip(),
                      chapter_id, problem_title)

    # 대화 초기화
    if st.session_state["sidebar_messages"]:
        if st.button("🗑 대화 지우기", key="clear_right",
                     use_container_width=True):
            st.session_state["sidebar_messages"] = []
            st.rerun()


def _send_message(api_key: str, message: str,
                  chapter_id: int = None, problem_title: str = None) -> None:
    """메시지를 GPT에 전송하고 응답을 받는다."""
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
