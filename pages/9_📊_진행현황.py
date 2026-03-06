"""진행현황 대시보드 페이지.

전체 학습 진행도, 챕터별 상세 현황, 학습 통계를 시각화하여 보여준다.
힌트 사용률, 문제별 시도 횟수 등 학습 패턴 분석 정보도 제공한다.
"""

import streamlit as st

from core.progress import ProgressManager
from ui.components import render_progress_bar
from ui.theme import apply_theme

st.set_page_config(
    page_title="진행현황 - 메타코드 파이썬 기초",
    page_icon="📊",
    layout="wide",
)

apply_theme()


def render_progress_page() -> None:
    """진행현황 전체 페이지를 렌더링한다.

    전체 요약, 챕터별 상세, 학습 통계 섹션으로 구성된다.
    """
    st.title("📊 학습 진행현황")
    st.markdown("지금까지의 학습 성과를 한눈에 확인하세요.")

    progress = ProgressManager()
    stats = progress.get_overall_stats()

    # ============================================================
    # 전체 요약 지표
    # ============================================================
    st.subheader("전체 요약")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pct = int(stats["overall_completion"] * 100)
        st.metric(
            "전체 완료율",
            f"{pct}%",
            help="전체 120문제 중 풀고 통과한 비율",
        )
    with col2:
        st.metric(
            "완료 문제 수",
            f"{stats['solved_problems']}개",
            help=f"전체 {stats['total_problems']}문제",
        )
    with col3:
        st.metric(
            "연속 학습",
            f"{stats['streak_days']}일",
            help="오늘 포함 매일 학습한 연속 일수",
        )
    with col4:
        st.metric(
            "오늘 풀은 문제",
            f"{stats['daily_solved']}개",
            help="오늘 목표: 3개",
        )

    render_progress_bar(stats["overall_completion"], "전체 진행도")

    st.divider()

    # ============================================================
    # 챕터별 상세 현황
    # ============================================================
    st.subheader("챕터별 상세 현황")

    chapter_info = [
        (1, "Python 소개"),
        (2, "데이터 타입"),
        (3, "자료형"),
        (4, "조건문/반복문"),
        (5, "함수/클래스"),
        (6, "파일 다루기"),
        (7, "예외 처리"),
        (8, "라이브러리"),
    ]

    for ch_id, ch_title in chapter_info:
        completion = stats["chapter_completions"].get(ch_id, 0.0)
        quiz_score = progress.get_chapter_quiz_score(ch_id)
        solved_count = int(completion * 15)
        quiz_count = int(quiz_score * 10)

        pct = int(completion * 100)

        col_title, col_bar, col_stats = st.columns([2, 4, 2])
        with col_title:
            icon = "✅" if pct == 100 else ("📖" if pct > 0 else "📌")
            st.markdown(f"**{icon} 챕터 {ch_id}: {ch_title}**")

        with col_bar:
            render_progress_bar(completion)

        with col_stats:
            st.caption(
                f"문제: {solved_count}/15 | 퀴즈: {quiz_count}/10"
            )

    st.divider()

    # ============================================================
    # 학습 통계 분석
    # ============================================================
    st.subheader("학습 통계")

    # 내부 데이터 로드
    raw_data = progress._data  # 내부 상태 직접 접근 (분석용)
    solved_problems = raw_data.get("solved_problems", {})

    if not solved_problems:
        st.info("아직 풀은 문제가 없습니다. 챕터를 선택하여 학습을 시작해보세요!")
        return

    # 총 시도 횟수
    total_attempts = sum(
        info.get("attempts", 0) for info in solved_problems.values()
    )

    # 힌트 사용률 계산
    hint_used_count = sum(
        1 for info in solved_problems.values() if info.get("hints_used", 0) > 0
    )
    total_solved = len(solved_problems)
    hint_rate = hint_used_count / total_solved if total_solved > 0 else 0.0

    # 평균 점수
    scores = [info.get("score", 0.0) for info in solved_problems.values()]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(
            "총 시도 횟수",
            f"{total_attempts}회",
            help="모든 문제의 제출 시도 횟수 합계",
        )
    with col_b:
        st.metric(
            "힌트 사용률",
            f"{int(hint_rate * 100)}%",
            help="힌트를 1개 이상 사용한 문제 비율",
        )
    with col_c:
        st.metric(
            "평균 점수",
            f"{int(avg_score * 100)}점",
            help="모든 풀이 문제의 평균 점수 (0~100)",
        )

    # 난이도별 현황
    st.markdown("**난이도별 풀이 현황**")

    difficulty_counts = {"basic": 0, "intermediate": 0, "advanced": 0}
    difficulty_labels = {"basic": "기초", "intermediate": "중급", "advanced": "심화"}

    # 문제 데이터에서 난이도 정보 추출
    import json
    from pathlib import Path

    data_dir = Path(__file__).parent.parent / "data" / "problems"

    for ch_id in range(1, 9):
        problems_file = data_dir / f"chapter{ch_id}_problems.json"
        if problems_file.exists():
            try:
                with open(problems_file, "r", encoding="utf-8") as f:
                    problems_data = json.load(f)
                    for p in problems_data.get("problems", []):
                        pid = p.get("problem_id", "")
                        diff = p.get("difficulty", "basic")
                        status = progress.get_problem_status(pid)
                        if status.get("solved"):
                            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            except Exception:
                pass

    diff_col1, diff_col2, diff_col3 = st.columns(3)
    with diff_col1:
        st.metric(
            "기초 문제",
            f"{difficulty_counts['basic']}개 완료",
            help="각 챕터당 기초 5문제 × 8챕터 = 40문제",
        )
    with diff_col2:
        st.metric(
            "중급 문제",
            f"{difficulty_counts['intermediate']}개 완료",
            help="각 챕터당 중급 5문제 × 8챕터 = 40문제",
        )
    with diff_col3:
        st.metric(
            "심화 문제",
            f"{difficulty_counts['advanced']}개 완료",
            help="각 챕터당 심화 5문제 × 8챕터 = 40문제",
        )

    st.divider()

    # ============================================================
    # 최근 학습 이력
    # ============================================================
    daily_log = raw_data.get("daily_log", [])

    if daily_log:
        st.subheader("학습 이력")
        recent_dates = sorted(daily_log, reverse=True)[:10]

        st.markdown("최근 학습일:")
        date_cols = st.columns(min(len(recent_dates), 5))
        for i, d in enumerate(recent_dates[:5]):
            with date_cols[i]:
                st.markdown(
                    f'<div style="text-align:center;background:#EBF8FF;'
                    f'border-radius:8px;padding:8px;font-size:0.85em;">'
                    f'📅 {d}</div>',
                    unsafe_allow_html=True,
                )


render_progress_page()
