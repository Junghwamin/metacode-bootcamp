"""재사용 가능한 UI 컴포넌트 모음.

진행도 바, 챕터 카드, 난이도 배지, 채점 결과 표시 등
여러 페이지에서 공통으로 사용하는 UI 요소를 정의한다.

디자인 시스템: Claymorphism + Minimal Swiss
- 카드 호버 리프트 효과 (translateY(-2px))
- 그라디언트 진행도 바
- 부드러운 섀도우 시스템
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
    Claymorphism 스타일: 부드러운 섀도우 + 호버 리프트 + 그라디언트 진행도 바.

    Args:
        chapter_id: 챕터 번호 (1~8)
        title: 챕터 제목
        description: 챕터 한 줄 설명
        completion: 완료율 (0.0 ~ 1.0)
    """
    pct = int(completion * 100)

    # 완료 상태에 따른 색상 및 레이블
    if pct == 100:
        # 완료: Fresh Green 그라디언트
        progress_gradient = "linear-gradient(90deg, #00C48C, #00A37A)"
        status_text = "완료"
        status_color = "#00C48C"
        top_accent = "#00C48C"
    elif pct > 0:
        # 진행 중: Trust Blue -> Vibrant Purple 그라디언트
        progress_gradient = "linear-gradient(90deg, #4A90D9, #6C63FF)"
        status_text = "진행 중"
        status_color = "#4A90D9"
        top_accent = "#4A90D9"
    else:
        # 미시작: 회색
        progress_gradient = "linear-gradient(90deg, #B2BEC3, #DFE6E9)"
        status_text = "시작 전"
        status_color = "#B2BEC3"
        top_accent = "#DFE6E9"

    with st.container():
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 0;
                border: 1px solid rgba(0,0,0,0.06);
                margin-bottom: 12px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
                overflow: hidden;
            "
            onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)';"
            onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)';"
            >
                <!-- 상단 액센트 바 -->
                <div style="
                    height: 3px;
                    background: {top_accent};
                    border-radius: 12px 12px 0 0;
                "></div>
                <!-- 카드 내용 -->
                <div style="padding: 14px 16px 12px;">
                    <!-- 챕터 번호 배지 + 제목 -->
                    <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 6px;">
                        <div style="
                            background: rgba(74,144,217,0.1);
                            color: #4A90D9;
                            border-radius: 8px;
                            padding: 3px 8px;
                            font-size: 0.72em;
                            font-weight: 700;
                            font-family: 'Inter', sans-serif;
                            white-space: nowrap;
                            flex-shrink: 0;
                            margin-top: 2px;
                        ">Ch.{chapter_id}</div>
                        <div style="
                            font-size: 0.95em;
                            font-weight: 700;
                            color: #2D3436;
                            line-height: 1.4;
                        ">{title}</div>
                    </div>
                    <!-- 설명 -->
                    <div style="
                        font-size: 0.8em;
                        color: #636E72;
                        margin-bottom: 10px;
                        line-height: 1.5;
                    ">{description}</div>
                    <!-- 진행도 바 -->
                    <div style="
                        background: rgba(0,0,0,0.07);
                        border-radius: 4px;
                        height: 5px;
                        overflow: hidden;
                        margin-bottom: 6px;
                    ">
                        <div style="
                            background: {progress_gradient};
                            width: {pct}%;
                            height: 100%;
                            border-radius: 4px;
                            transition: width 0.4s ease;
                        "></div>
                    </div>
                    <!-- 완료율 + 상태 -->
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="
                            font-size: 0.75em;
                            color: #636E72;
                            font-family: 'Inter', sans-serif;
                        ">{pct}% 완료</span>
                        <span style="
                            font-size: 0.72em;
                            font-weight: 600;
                            color: {status_color};
                            font-family: 'Inter', sans-serif;
                        ">{status_text}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_difficulty_badge(difficulty: str) -> str:
    """난이도 배지 HTML을 반환한다.

    새로운 Education/Tech 팔레트 적용:
    - 기초: Fresh Green (#00C48C)
    - 중급: Warm Amber (#FFB946)
    - 심화: Coral (#FF6B6B)

    Args:
        difficulty: "basic" | "intermediate" | "advanced"

    Returns:
        str: 난이도 배지 HTML 문자열
    """
    badges = {
        "basic": (
            '<span style="background:rgba(0,196,140,0.12);color:#00C48C;'
            'border:1.5px solid rgba(0,196,140,0.35);'
            'padding:2px 10px;border-radius:20px;font-size:0.78em;font-weight:700;'
            'font-family:Inter,sans-serif;letter-spacing:0.02em;">'
            '★ 기초</span>'
        ),
        "intermediate": (
            '<span style="background:rgba(255,185,70,0.12);color:#B8860B;'
            'border:1.5px solid rgba(255,185,70,0.35);'
            'padding:2px 10px;border-radius:20px;font-size:0.78em;font-weight:700;'
            'font-family:Inter,sans-serif;letter-spacing:0.02em;">'
            '★★ 중급</span>'
        ),
        "advanced": (
            '<span style="background:rgba(255,107,107,0.12);color:#FF6B6B;'
            'border:1.5px solid rgba(255,107,107,0.35);'
            'padding:2px 10px;border-radius:20px;font-size:0.78em;font-weight:700;'
            'font-family:Inter,sans-serif;letter-spacing:0.02em;">'
            '★★★ 심화</span>'
        ),
    }
    return badges.get(difficulty, badges["basic"])


def render_grade_result(passed: bool, score: float, feedback: str) -> None:
    """채점 결과를 렌더링한다.

    통과/부분점수/실패에 따라 다른 색상의 박스를 표시한다.
    Claymorphism 스타일: 부드러운 배경 + 컬러 보더 + 아이콘.

    Args:
        passed: 통과 여부
        score: 획득 점수 (0.0 ~ 1.0)
        feedback: 한국어 피드백 메시지
    """
    pct = int(score * 100)

    if passed:
        # 정답: Fresh Green 계열
        bg_color = "rgba(0, 196, 140, 0.06)"
        border_color = "#00C48C"
        title_color = "#00865A"
        icon_html = '<span style="color:#00C48C;font-size:1.2em;">✓</span>'
        title = f"정답입니다! ({pct}점)"
    elif score > 0:
        # 부분 점수: Warm Amber 계열
        bg_color = "rgba(255, 185, 70, 0.06)"
        border_color = "#FFB946"
        title_color = "#B8860B"
        icon_html = '<span style="font-family:Inter;font-size:1em;color:#FFB946;">◑</span>'
        title = f"부분 점수 ({pct}점)"
    else:
        # 실패: Coral 계열 (겁주지 않는 디자인 - 따뜻한 빨강)
        bg_color = "rgba(255, 107, 107, 0.06)"
        border_color = "#FF6B6B"
        title_color = "#E53E3E"
        icon_html = '<span style="color:#FF6B6B;font-size:1.1em;">○</span>'
        title = f"아직 더 해봐요! ({pct}점)"

    st.markdown(
        f"""
        <div style="
            background: {bg_color};
            border: 2px solid {border_color};
            border-radius: 12px;
            padding: 16px 20px;
            margin: 8px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        ">
            <div style="
                font-weight: 700;
                font-size: 1.05em;
                margin-bottom: 8px;
                color: {title_color};
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                {icon_html} {title}
            </div>
            <div style="
                white-space: pre-wrap;
                font-size: 0.9em;
                color: #2D3436;
                line-height: 1.6;
            ">{feedback}</div>
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

    Claymorphism 스타일: Warm Amber 배경 + 부드러운 보더.

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
                # 힌트 레벨에 따른 강도 색상 (가벼울수록 밝은 색)
                intensity = min(i * 0.15 + 0.08, 0.18)
                st.markdown(
                    f'<div style="background:rgba(255,185,70,{intensity});'
                    f'border:1.5px solid rgba(255,185,70,0.4);border-radius:12px;'
                    f'padding:12px 16px;margin:6px 0;">'
                    f'<div style="font-weight:700;color:#B8860B;margin-bottom:4px;font-size:0.88em;">'
                    f'힌트 {i+1} - {label}</div>'
                    f'<span style="color:#78350F;font-size:0.9em;line-height:1.6;">{hint_content}</span></div>',
                    unsafe_allow_html=True,
                )

        # 다음 힌트 버튼
        if hints_used < len(hints):
            remaining = len(hints) - hints_used
            if on_hint_callback and st.button(f"힌트 보기 ({remaining}개 남음)"):
                on_hint_callback(hints_used + 1)
        return

    # 단순 텍스트 표시 모드
    level_labels = {1: "가벼운 힌트", 2: "구체적 힌트", 3: "거의 정답"}
    label = level_labels.get(level, f"힌트 {level}")

    st.markdown(
        f"""
        <div style="
            background: rgba(255, 185, 70, 0.08);
            border: 1.5px solid rgba(255, 185, 70, 0.4);
            border-radius: 12px;
            padding: 12px 16px;
            margin: 8px 0;
        ">
            <div style="font-weight: 700; color: #B8860B; margin-bottom: 4px; font-size: 0.88em;">
                힌트 {level} - {label}
            </div>
            <div style="color: #78350F; font-size: 0.9em; line-height: 1.6;">{hint_text}</div>
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
    성공: 깔끔한 코드 블록, 실패: Warm Amber 겁주지 않는 에러 디자인.

    Args:
        result: 실행 결과 딕셔너리
                {"success": bool, "output": str, "error": str, "translated": str}
    """
    if result.get("success", False):
        output = result.get("output", result.get("stdout", ""))
        if output:
            st.markdown(
                '<div style="font-size:0.85em;font-weight:600;color:#636E72;'
                'margin-bottom:4px;text-transform:uppercase;letter-spacing:0.05em;'
                'font-family:Inter,sans-serif;">실행 결과</div>',
                unsafe_allow_html=True,
            )
            st.code(output, language="text")
        else:
            st.markdown(
                '<div style="background:rgba(0,196,140,0.08);border:1.5px solid rgba(0,196,140,0.3);'
                'border-radius:12px;padding:10px 16px;color:#00865A;font-size:0.9em;">'
                '실행 완료 (출력 없음)</div>',
                unsafe_allow_html=True,
            )
    else:
        error = result.get("translated", result.get("stderr", result.get("error", "오류 발생")))
        st.markdown(
            f'<div style="background:rgba(255,185,70,0.08);border:1.5px solid rgba(255,185,70,0.4);'
            f'border-radius:12px;padding:14px 16px;margin:8px 0;">'
            f'<div style="font-weight:700;color:#B45309;margin-bottom:6px;font-size:0.95em;">'
            f'오류 발생</div>'
            f'<code style="color:#78350F;font-size:0.88em;line-height:1.6;white-space:pre-wrap;">'
            f'{error}</code></div>',
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

        if st.button(label, key=f"nav_prob_{i}_{pid}", use_container_width=True):
            new_idx = i

    return new_idx
