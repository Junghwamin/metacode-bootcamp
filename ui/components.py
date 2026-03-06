"""재사용 가능한 UI 컴포넌트 모음.

진행도 바, 챕터 카드, 난이도 배지, 채점 결과 표시 등
여러 페이지에서 공통으로 사용하는 UI 요소를 정의한다.
"""

import streamlit as st


def render_progress_bar(completion: float, label: str = "") -> None:
    """진행도 바를 렌더링한다.

    Streamlit의 progress()를 감싸서 레이블과 퍼센트를 같이 보여준다.

    Args:
        completion: 완료율 (0.0 ~ 1.0)
        label: 진행도 바 위에 표시할 레이블 텍스트
    """
    pct = int(completion * 100)

    col1, col2 = st.columns([4, 1])
    with col1:
        if label:
            st.caption(label)
    with col2:
        st.caption(f"{pct}%")

    st.progress(min(completion, 1.0))


def render_chapter_card(
    chapter_id: int,
    title: str,
    description: str,
    completion: float,
) -> None:
    """챕터 카드를 렌더링한다.

    챕터 번호, 제목, 설명, 완료율을 하나의 카드로 표시한다.

    Args:
        chapter_id: 챕터 번호 (1~8)
        title: 챕터 제목
        description: 챕터 한 줄 설명
        completion: 완료율 (0.0 ~ 1.0)
    """
    pct = int(completion * 100)

    # 완료 상태에 따른 아이콘
    if pct == 100:
        status_icon = "✅"
    elif pct > 0:
        status_icon = "📖"
    else:
        status_icon = "📌"

    with st.container():
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #E2E8F0;
                margin-bottom: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            ">
                <div style="font-size: 1.1em; font-weight: 700; margin-bottom: 4px;">
                    {status_icon} 챕터 {chapter_id}: {title}
                </div>
                <div style="font-size: 0.85em; color: #718096; margin-bottom: 8px;">
                    {description}
                </div>
                <div style="
                    background: #E2E8F0;
                    border-radius: 4px;
                    height: 6px;
                    overflow: hidden;
                ">
                    <div style="
                        background: {'#48BB78' if pct == 100 else '#4A90D9'};
                        width: {pct}%;
                        height: 100%;
                        border-radius: 4px;
                        transition: width 0.3s ease;
                    "></div>
                </div>
                <div style="font-size: 0.8em; color: #718096; margin-top: 4px; text-align: right;">
                    {pct}% 완료
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_difficulty_badge(difficulty: str) -> str:
    """난이도 배지 HTML을 반환한다.

    Args:
        difficulty: "basic" | "intermediate" | "advanced"

    Returns:
        str: 난이도 배지 HTML 문자열
    """
    badges = {
        "basic": ('<span style="background:#ECFDF5;color:#48BB78;border:1px solid #48BB78;'
                  'padding:2px 8px;border-radius:10px;font-size:0.82em;font-weight:700;">'
                  '★ 기초</span>'),
        "intermediate": ('<span style="background:#FFF7ED;color:#ED8936;border:1px solid #ED8936;'
                         'padding:2px 8px;border-radius:10px;font-size:0.82em;font-weight:700;">'
                         '★★ 중급</span>'),
        "advanced": ('<span style="background:#FFF5F5;color:#F56565;border:1px solid #F56565;'
                     'padding:2px 8px;border-radius:10px;font-size:0.82em;font-weight:700;">'
                     '★★★ 심화</span>'),
    }
    return badges.get(difficulty, badges["basic"])


def render_grade_result(passed: bool, score: float, feedback: str) -> None:
    """채점 결과를 렌더링한다.

    통과/부분점수/실패에 따라 다른 색상의 박스를 표시한다.

    Args:
        passed: 통과 여부
        score: 획득 점수 (0.0 ~ 1.0)
        feedback: 한국어 피드백 메시지
    """
    pct = int(score * 100)

    if passed:
        bg_color = "#F0FFF4"
        border_color = "#48BB78"
        icon = "✅"
        title = f"정답입니다! ({pct}점)"
    elif score > 0:
        bg_color = "#FFFAF0"
        border_color = "#ED8936"
        icon = "📊"
        title = f"부분 점수 ({pct}점)"
    else:
        bg_color = "#FFF5F5"
        border_color = "#F56565"
        icon = "❌"
        title = f"아직 더 해봐요! ({pct}점)"

    st.markdown(
        f"""
        <div style="
            background: {bg_color};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 16px;
            margin: 8px 0;
        ">
            <div style="font-weight: 700; font-size: 1.05em; margin-bottom: 8px;">
                {icon} {title}
            </div>
            <div style="white-space: pre-wrap; font-size: 0.9em;">{feedback}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hint_panel(hint_text: str = "", level: int = 1, problem: dict = None,
                       hints_used: int = 0, on_hint_callback=None) -> None:
    """힌트 패널을 렌더링한다.

    두 가지 호출 방식을 모두 지원한다:
    1. render_hint_panel(hint_text, level) - 단순 텍스트 표시
    2. render_hint_panel(problem=p, hints_used=n, on_hint_callback=cb) - 풀 힌트 시스템

    Args:
        hint_text: 힌트 내용 (단순 표시 모드)
        level: 힌트 레벨 (1, 2, 3)
        problem: 문제 딕셔너리 (풀 힌트 시스템 모드)
        hints_used: 사용한 힌트 수 (풀 힌트 시스템 모드)
        on_hint_callback: 힌트 클릭 콜백 함수 (풀 힌트 시스템 모드)
    """
    # 풀 힌트 시스템 모드
    if problem is not None:
        hints = problem.get("hints", [])
        if not hints:
            return

        st.markdown("**힌트**")

        # 이미 열린 힌트 표시
        for i in range(hints_used):
            if i < len(hints):
                hint_item = hints[i]
                hint_content = hint_item.get("text", "") if isinstance(hint_item, dict) else str(hint_item)
                level_labels = {0: "가벼운 힌트", 1: "구체적 힌트", 2: "거의 정답"}
                label = level_labels.get(i, f"힌트 {i+1}")
                st.markdown(
                    f'<div style="background:#FFFFF0;border:1px solid #F6E05E;border-radius:8px;'
                    f'padding:10px 14px;margin:6px 0;"><strong>💡 힌트 {i+1} - {label}</strong><br>'
                    f'<span style="color:#744210;">{hint_content}</span></div>',
                    unsafe_allow_html=True,
                )

        # 다음 힌트 버튼
        if hints_used < len(hints):
            remaining = len(hints) - hints_used
            if on_hint_callback and st.button(f"💡 힌트 보기 ({remaining}개 남음)"):
                on_hint_callback(hints_used + 1)
        return

    # 단순 텍스트 표시 모드
    level_labels = {1: "가벼운 힌트", 2: "구체적 힌트", 3: "거의 정답"}
    label = level_labels.get(level, f"힌트 {level}")

    st.markdown(
        f"""
        <div style="
            background: #FFFFF0;
            border: 1px solid #F6E05E;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px 0;
        ">
            <div style="font-weight: 700; color: #744210; margin-bottom: 4px;">
                💡 힌트 {level} - {label}
            </div>
            <div style="color: #744210; font-size: 0.9em;">{hint_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_code_editor(key: str, initial_code: str = "", height: int = 300) -> str:
    """코드 에디터를 렌더링한다.

    streamlit-code-editor가 없으면 st.text_area로 폴백한다.

    Args:
        key: 에디터 고유 키
        initial_code: 초기 코드 문자열
        height: 에디터 높이 (픽셀)

    Returns:
        str: 현재 에디터의 코드 내용
    """
    code = st.text_area(
        "코드 에디터",
        value=initial_code,
        height=height,
        key=key,
        label_visibility="collapsed",
    )
    return code


def render_execution_result(result: dict) -> None:
    """코드 실행 결과를 렌더링한다.

    성공/실패에 따라 다른 스타일로 표시한다.

    Args:
        result: 실행 결과 딕셔너리
                {"success": bool, "output": str, "error": str, "translated": str}
    """
    if result.get("success", False):
        output = result.get("output", result.get("stdout", ""))
        if output:
            st.markdown("**실행 결과:**")
            st.code(output, language="text")
        else:
            st.info("출력 없음 (실행 완료)")
    else:
        error = result.get("translated", result.get("stderr", result.get("error", "오류 발생")))
        st.markdown(
            f'<div style="background:#FFFBEB;border:1px solid #F6AD55;border-radius:8px;'
            f'padding:12px;margin:8px 0;"><strong style="color:#C05621;">오류 발생</strong><br>'
            f'<code style="color:#744210;">{error}</code></div>',
            unsafe_allow_html=True,
        )


def render_problem_navigation(
    problems: list, current_idx: int, progress: dict = None
) -> int:
    """문제 목록 네비게이션을 렌더링하고 선택된 인덱스를 반환한다.

    Args:
        problems: 문제 딕셔너리 목록
        current_idx: 현재 선택된 인덱스
        progress: 진행도 딕셔너리 {"completed_problems": [problem_id, ...]}

    Returns:
        int: 새로 선택된 문제 인덱스
    """
    completed = set(progress.get("completed_problems", []) if progress else [])

    st.markdown("**문제 목록**")
    new_idx = current_idx

    for i, problem in enumerate(problems):
        pid = problem.get("problem_id", problem.get("id", f"p{i}"))
        title = problem.get("title", f"문제 {i+1}")
        difficulty = problem.get("difficulty", "basic")

        is_done = pid in completed
        icon = "✅" if is_done else "○"
        diff_short = {"basic": "기초", "intermediate": "중급", "advanced": "심화"}.get(difficulty, "")

        label = f"{icon} {i+1}. {title} [{diff_short}]"
        style = "font-weight:700;color:#4A90D9;" if i == current_idx else ""

        if st.button(label, key=f"nav_prob_{i}_{pid}", use_container_width=True):
            new_idx = i

    return new_idx
