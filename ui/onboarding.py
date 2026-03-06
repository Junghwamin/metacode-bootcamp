"""온보딩 UI 모듈.

앱 첫 방문자에게 플랫폼 사용법을 안내한다.
세션 상태로 온보딩 완료 여부를 추적한다.
"""

import streamlit as st


def show_onboarding() -> None:
    """온보딩 화면을 표시한다.

    세션 상태의 onboarding_done이 False이거나 없으면
    사이드바에 시작 안내를 표시한다.
    """
    if "onboarding_done" not in st.session_state:
        st.session_state["onboarding_done"] = False

    if st.session_state.get("onboarding_done"):
        return

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 처음 오셨나요?")
        st.markdown("""
        **메타코드 파이썬 기초**에 오신 것을 환영합니다!

        학습 순서:
        1. 왼쪽 사이드바에서 챕터 선택
        2. 개념 학습 (설명 + 코드 예제)
        3. 문제 풀기 (15문제/챕터)
        4. 퀴즈로 마무리 (10문제/챕터)
        """)

        if st.button("시작하기!", use_container_width=True):
            st.session_state["onboarding_done"] = True
            st.rerun()
