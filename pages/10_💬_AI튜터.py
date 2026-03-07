"""AI 튜터 페이지.

GPT 기반 챗봇으로 학습 중 막히는 부분을 질문할 수 있다.
정답을 직접 알려주지 않고, 힌트와 설명으로 가르친다.
"""

import streamlit as st
from ui.theme import apply_theme

st.set_page_config(
    page_title="AI 튜터",
    page_icon="💬",
    layout="wide",
)

apply_theme()

# === API 키 로드 ===
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.title("💬 AI 튜터")
    st.warning("AI 튜터 기능을 사용하려면 관리자가 API 키를 설정해야 합니다.")
    st.stop()

# === 모듈 임포트 (API 키 확인 후) ===
from core.chatbot import chat_with_tutor  # noqa: E402

# === 페이지 헤더 ===
st.title("💬 AI 튜터")
st.caption("Python 학습 중 궁금한 점을 물어보세요. 정답 대신 힌트와 설명으로 도와드립니다.")

# === 사이드바: 컨텍스트 설정 ===
with st.sidebar:
    st.markdown("### 학습 컨텍스트")
    st.caption("현재 학습 중인 내용을 선택하면 더 정확한 답변을 받을 수 있어요.")

    chapter_id = st.selectbox(
        "챕터",
        options=[None, 1, 2, 3, 4, 5, 6, 7, 8],
        format_func=lambda x: "선택 안 함" if x is None else f"챕터 {x}",
        index=0,
    )

    problem_title = st.text_input(
        "문제 제목 (선택)",
        placeholder="예: 리스트 정렬하기",
    )

    user_code = st.text_area(
        "내 코드 (선택)",
        placeholder="질문하고 싶은 코드를 붙여넣으세요",
        height=120,
    )

    error_msg = st.text_area(
        "에러 메시지 (선택)",
        placeholder="에러가 났다면 여기에 붙여넣으세요",
        height=80,
    )

    # 일일 사용량 제한 (localStorage 대신 session_state로 관리)
    if "chat_count" not in st.session_state:
        st.session_state["chat_count"] = 0

    remaining = max(0, 30 - st.session_state["chat_count"])
    st.markdown(f"오늘 남은 질문: **{remaining}회**")

    if st.button("대화 초기화", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.rerun()

# === 대화 기록 초기화 ===
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# === 빠른 질문 버튼 ===
st.markdown("**빠른 질문:**")
quick_cols = st.columns(4)
quick_questions = [
    "이 개념이 이해가 안 돼요",
    "에러가 났는데 도와주세요",
    "내 코드를 리뷰해 주세요",
    "힌트를 주세요",
]

for i, q in enumerate(quick_questions):
    with quick_cols[i]:
        if st.button(q, key=f"quick_{i}", use_container_width=True):
            # 컨텍스트에 따라 질문 보강
            full_q = q
            if q == "에러가 났는데 도와주세요" and error_msg:
                full_q = f"에러가 났어요: {error_msg[:200]}"
            elif q == "내 코드를 리뷰해 주세요" and user_code:
                full_q = f"내 코드를 리뷰해 주세요:\n```python\n{user_code[:300]}\n```"

            st.session_state["chat_messages"].append({"role": "user", "content": full_q})

            if st.session_state["chat_count"] < 30:
                with st.spinner("생각하는 중..."):
                    try:
                        reply = chat_with_tutor(
                            st.session_state["chat_messages"],
                            api_key,
                            chapter_id=chapter_id,
                            problem_title=problem_title or None,
                            user_code=user_code or None,
                            error_msg=error_msg or None,
                        )
                        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
                        st.session_state["chat_count"] += 1
                    except Exception as e:
                        st.session_state["chat_messages"].append({
                            "role": "assistant",
                            "content": f"죄송합니다, 오류가 발생했습니다: {str(e)[:100]}"
                        })
            st.rerun()

st.divider()

# === 대화 표시 ===
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === 입력창 ===
if prompt := st.chat_input("Python에 대해 궁금한 점을 물어보세요..."):
    if st.session_state["chat_count"] >= 30:
        st.error("오늘의 질문 횟수(30회)를 모두 사용했습니다. 내일 다시 이용해 주세요!")
    else:
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("생각하는 중..."):
                try:
                    reply = chat_with_tutor(
                        st.session_state["chat_messages"],
                        api_key,
                        chapter_id=chapter_id,
                        problem_title=problem_title or None,
                        user_code=user_code or None,
                        error_msg=error_msg or None,
                    )
                    st.markdown(reply)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
                    st.session_state["chat_count"] += 1
                except Exception as e:
                    error_text = f"죄송합니다, 오류가 발생했습니다: {str(e)[:100]}"
                    st.markdown(error_text)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": error_text})
