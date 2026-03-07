"""온보딩 UI 모듈.

앱 첫 방문자에게 플랫폼 사용법을 안내한다.
세션 상태로 온보딩 완료 여부를 추적한다.

디자인: 센터 정렬 웰컴 카드 + 스텝 인디케이터 + 클리너 타이포그래피
"""

import streamlit as st


def show_onboarding() -> None:
    """온보딩 화면을 표시한다.

    세션 상태의 onboarding_done이 False이거나 없으면
    사이드바에 시작 안내를 표시한다.
    Claymorphism 스타일: 카드형 레이아웃 + 스텝 인디케이터 + 부드러운 배경.
    """
    if "onboarding_done" not in st.session_state:
        st.session_state["onboarding_done"] = False

    if st.session_state.get("onboarding_done"):
        return

    with st.sidebar:
        st.markdown("---")

        # 웰컴 카드 헤더
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, rgba(74,144,217,0.08), rgba(108,99,255,0.08));
                border: 1.5px solid rgba(74,144,217,0.2);
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
            ">
                <div style="
                    font-size: 1em;
                    font-weight: 700;
                    color: #2D3436;
                    margin-bottom: 4px;
                ">처음 오셨나요?</div>
                <div style="
                    font-size: 0.82em;
                    color: #636E72;
                    line-height: 1.5;
                ">메타코드 파이썬 기초에 오신 것을 환영합니다.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 스텝 인디케이터 (4단계)
        st.markdown(
            """
            <div style="display: flex; justify-content: center; gap: 6px; margin-bottom: 14px;">
                <div style="
                    width: 28px; height: 4px; border-radius: 2px;
                    background: #4A90D9;
                "></div>
                <div style="
                    width: 28px; height: 4px; border-radius: 2px;
                    background: rgba(0,0,0,0.1);
                "></div>
                <div style="
                    width: 28px; height: 4px; border-radius: 2px;
                    background: rgba(0,0,0,0.1);
                "></div>
                <div style="
                    width: 28px; height: 4px; border-radius: 2px;
                    background: rgba(0,0,0,0.1);
                "></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 학습 순서 - 번호 배지 스타일
        steps = [
            ("1", "챕터 선택", "왼쪽 사이드바에서 챕터를 선택하세요."),
            ("2", "개념 학습", "설명과 코드 예제로 개념을 익히세요."),
            ("3", "문제 풀기", "챕터당 15개의 연습 문제를 풀어보세요."),
            ("4", "퀴즈 마무리", "10문제 퀴즈로 학습을 완성하세요."),
        ]

        for num, title, desc in steps:
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    gap: 10px;
                    align-items: flex-start;
                    margin-bottom: 10px;
                ">
                    <div style="
                        background: linear-gradient(135deg, #4A90D9, #6C63FF);
                        color: white;
                        border-radius: 8px;
                        width: 22px;
                        height: 22px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 0.72em;
                        font-weight: 700;
                        font-family: Inter, sans-serif;
                        flex-shrink: 0;
                        margin-top: 1px;
                    ">{num}</div>
                    <div>
                        <div style="font-size: 0.85em; font-weight: 600; color: #2D3436; margin-bottom: 1px;">{title}</div>
                        <div style="font-size: 0.78em; color: #636E72; line-height: 1.4;">{desc}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        if st.button("시작하기", use_container_width=True, type="primary"):
            st.session_state["onboarding_done"] = True
            st.rerun()
