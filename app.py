"""메타코드 파이썬 기초 - 메인 대시보드.

전체 학습 진행도, 챕터별 완료율, 스트릭, 일일 목표를 표시한다.
챕터 카드 그리드로 빠른 이동을 지원하고,
진행도 내보내기/가져오기로 데이터를 보존할 수 있다.

디자인 시스템: Claymorphism + Minimal Swiss
- 커스텀 HTML 메트릭 카드 (st.metric 대신)
- 그라디언트 헤더
- 클리너 챕터 그리드
"""

import streamlit as st

# ============================================================
# 페이지 설정 - 반드시 가장 먼저 실행해야 한다
# ============================================================
st.set_page_config(
    page_title="메타코드 파이썬 기초",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 테마 적용 (Google Fonts, 커스텀 CSS)
from ui.theme import apply_theme
apply_theme()

# AI 튜터 채팅 패널 (오른쪽 컬럼, 모든 페이지 공통)
from ui.chat_sidebar import render_chat_panel
content = render_chat_panel()

# 온보딩 체크 (처음 방문자에게 안내 - 사이드바 사용이므로 content 밖에서 실행)
from ui.onboarding import show_onboarding
show_onboarding()

# 진행도 관리
from core.progress import ProgressManager
from ui.components import render_chapter_card, render_progress_bar


def render_metric_cards(stats: dict) -> None:
    """커스텀 HTML 메트릭 카드 3개를 렌더링한다.

    st.metric 대신 커스텀 HTML을 사용하여 Claymorphism 스타일 적용.
    호버 리프트 효과 + 그라디언트 값 색상.

    Args:
        stats: ProgressManager.get_overall_stats() 반환값 딕셔너리
    """
    col1, col2, col3 = st.columns(3)

    metrics = [
        {
            "label": "완료한 문제",
            "value": f"{stats['solved_problems']}/{stats['total_problems']}",
            "sub": "지금까지 풀고 통과한 문제",
            "color": "#4A90D9",
            "bg": "rgba(74, 144, 217, 0.06)",
            "border": "rgba(74, 144, 217, 0.2)",
        },
        {
            "label": "연속 학습",
            "value": f"{stats['streak_days']}일",
            "sub": "오늘 포함 매일 학습한 연속 일수",
            "color": "#6C63FF",
            "bg": "rgba(108, 99, 255, 0.06)",
            "border": "rgba(108, 99, 255, 0.2)",
        },
        {
            "label": "오늘 목표",
            "value": f"{stats['daily_solved']}/3",
            "sub": "오늘 목표: 문제 3개 풀기",
            "color": "#00C48C",
            "bg": "rgba(0, 196, 140, 0.06)",
            "border": "rgba(0, 196, 140, 0.2)",
        },
    ]

    for col, m in zip([col1, col2, col3], metrics):
        with col:
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 20px 24px;
                    border: 1px solid {m['border']};
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.08);
                    transition: all 0.2s ease;
                    background: {m['bg']};
                "
                onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)';"
                onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.08)';"
                >
                    <div style="
                        font-size: 0.72em;
                        font-weight: 600;
                        color: #636E72;
                        text-transform: uppercase;
                        letter-spacing: 0.07em;
                        font-family: 'Inter', sans-serif;
                        margin-bottom: 8px;
                    ">{m['label']}</div>
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: {m['color']};
                        font-family: 'Inter', sans-serif;
                        line-height: 1.1;
                        margin-bottom: 6px;
                    ">{m['value']}</div>
                    <div style="
                        font-size: 0.78em;
                        color: #636E72;
                        line-height: 1.4;
                    ">{m['sub']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    """메인 대시보드를 렌더링한다.

    전체 진행도 통계, 챕터 카드 그리드, 진행도 내보내기/가져오기를 표시한다.
    """
    # ============================================================
    # 헤더: 그라디언트 서브타이틀 + 깔끔한 타이포그래피
    # ============================================================
    st.markdown(
        """
        <div style="margin-bottom: 8px;">
            <h1 style="
                font-size: 1.875rem;
                font-weight: 700;
                color: #2D3436;
                margin: 0 0 6px 0;
                line-height: 1.3;
            ">메타코드 파이썬 기초</h1>
            <p style="
                font-size: 1rem;
                color: #636E72;
                margin: 0;
                line-height: 1.6;
            ">프로그래밍을 처음 시작하는 당신을 위한 인터랙티브 학습 플랫폼</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    progress = ProgressManager()
    stats = progress.get_overall_stats()

    # ============================================================
    # 전체 현황 지표 3개: 커스텀 HTML 메트릭 카드
    # ============================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    render_metric_cards(stats)
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 전체 진행도 바
    render_progress_bar(stats["overall_completion"], "전체 진행도")

    st.divider()

    # ============================================================
    # 챕터 카드 그리드 (4열 × 2행)
    # ============================================================
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 1.25rem; font-weight: 700; color: #2D3436; margin: 0 0 4px 0;">
                챕터별 학습
            </h2>
            <p style="font-size: 0.85em; color: #636E72; margin: 0;">
                챕터를 선택하여 학습을 시작하세요. 순서대로 학습을 권장합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 챕터 정보: (id, 제목, 한 줄 설명)
    chapters = [
        (1, "Python 소개", "주석, 변수, print, input"),
        (2, "데이터 타입", "Number, String, Boolean"),
        (3, "자료형", "List, Tuple, Set, Dict"),
        (4, "조건문/반복문", "if, for, while"),
        (5, "함수/클래스", "def, class, 상속"),
        (6, "파일 다루기", "open, read, write"),
        (7, "예외 처리", "try, except, finally"),
        (8, "라이브러리", "NumPy, Pandas"),
    ]

    # 4열 그리드로 챕터 카드 배치
    cols = st.columns(4)
    for i, (ch_id, title, desc) in enumerate(chapters):
        completion = stats["chapter_completions"].get(ch_id, 0.0)
        with cols[i % 4]:
            render_chapter_card(ch_id, title, desc, completion)

    st.divider()

    # ============================================================
    # AI 튜터 링크 배너
    # ============================================================
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(108,99,255,0.08), rgba(74,144,217,0.08));
            border: 1.5px solid rgba(108,99,255,0.2);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        ">
            <div style="
                background: linear-gradient(135deg, #6C63FF, #4A90D9);
                border-radius: 10px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            ">
                <span style="color:white;font-size:1.2em;">AI</span>
            </div>
            <div>
                <div style="font-weight: 700; color: #2D3436; margin-bottom: 2px; font-size: 0.95em;">
                    AI 튜터와 함께 학습하기
                </div>
                <div style="font-size: 0.82em; color: #636E72;">
                    왼쪽 사이드바에서 AI 튜터 페이지를 열어 질문하고 개념을 확인하세요.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # 진행도 내보내기 / 가져오기
    # ============================================================
    st.markdown(
        """
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 1.1rem; font-weight: 700; color: #2D3436; margin: 0 0 4px 0;">
                진행도 관리
            </h2>
            <p style="font-size: 0.82em; color: #636E72; margin: 0;">
                브라우저가 바뀌거나 초기화되어도 진행도를 보존할 수 있습니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_exp, col_imp = st.columns(2)

    with col_exp:
        st.markdown("**진행도 내보내기**")
        if st.button("JSON으로 내보내기", use_container_width=True):
            export_data = progress.export_progress()
            st.download_button(
                label="다운로드",
                data=export_data,
                file_name="metacode_progress.json",
                mime="application/json",
                use_container_width=True,
            )

    with col_imp:
        st.markdown("**진행도 가져오기**")
        uploaded = st.file_uploader(
            "JSON 파일 업로드",
            type="json",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            json_str = uploaded.read().decode("utf-8")
            if st.button("가져오기", use_container_width=True):
                if progress.import_progress(json_str):
                    st.success("진행도를 성공적으로 가져왔습니다!")
                    st.rerun()
                else:
                    st.error("진행도 파일 형식이 올바르지 않습니다.")

    st.divider()

    # ============================================================
    # 진행도 초기화 (위험 작업 - 확인 버튼 필요)
    # ============================================================
    with st.expander("고급 설정", expanded=False):
        st.warning("진행도를 초기화하면 모든 풀이 기록이 삭제됩니다. 이 작업은 되돌릴 수 없습니다.")

        if "reset_confirm" not in st.session_state:
            st.session_state["reset_confirm"] = False

        if not st.session_state["reset_confirm"]:
            if st.button("진행도 초기화", type="secondary"):
                st.session_state["reset_confirm"] = True
                st.rerun()
        else:
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("네, 초기화합니다", type="primary"):
                    progress.reset_progress()
                    st.session_state["reset_confirm"] = False
                    st.success("진행도가 초기화되었습니다.")
                    st.rerun()
            with col_no:
                if st.button("취소"):
                    st.session_state["reset_confirm"] = False
                    st.rerun()


if __name__ == "__main__":
    with content:
        main()
