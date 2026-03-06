"""메타코드 파이썬 기초 - 메인 대시보드.

전체 학습 진행도, 챕터별 완료율, 스트릭, 일일 목표를 표시한다.
챕터 카드 그리드로 빠른 이동을 지원하고,
진행도 내보내기/가져오기로 데이터를 보존할 수 있다.
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

# 온보딩 체크 (처음 방문자에게 안내)
from ui.onboarding import show_onboarding
show_onboarding()

# 진행도 관리
from core.progress import ProgressManager
from ui.components import render_chapter_card, render_progress_bar


def main() -> None:
    """메인 대시보드를 렌더링한다.

    전체 진행도 통계, 챕터 카드 그리드, 진행도 내보내기/가져오기를 표시한다.
    """
    st.title("메타코드 파이썬 기초")
    st.markdown("프로그래밍을 처음 시작하는 당신을 위한 인터랙티브 학습 플랫폼")

    progress = ProgressManager()
    stats = progress.get_overall_stats()

    # ============================================================
    # 전체 현황 지표 3개: 완료 문제, 연속 학습, 일일 목표
    # ============================================================
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="완료한 문제",
            value=f"{stats['solved_problems']}/{stats['total_problems']}",
            help="지금까지 풀고 통과한 문제 수입니다.",
        )
    with col2:
        st.metric(
            label="연속 학습",
            value=f"{stats['streak_days']}일",
            help="오늘 포함 매일 학습한 연속 일수입니다.",
        )
    with col3:
        st.metric(
            label="오늘 목표",
            value=f"{stats['daily_solved']}/3",
            help="오늘 목표는 문제 3개 풀기입니다.",
        )

    # 전체 진행도 바
    render_progress_bar(stats["overall_completion"], "전체 진행도")

    st.divider()

    # ============================================================
    # 챕터 카드 그리드 (4열 × 2행)
    # ============================================================
    st.subheader("챕터별 학습")

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
    # 진행도 내보내기 / 가져오기
    # ============================================================
    st.subheader("진행도 관리")
    st.caption("브라우저가 바뀌거나 초기화되어도 진행도를 보존할 수 있습니다.")

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
    main()
