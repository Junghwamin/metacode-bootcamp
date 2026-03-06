"""앱 테마 및 스타일 정의.

Noto Sans KR 폰트, 초보자 친화적 색상, 접근성 고려.
Streamlit st.markdown으로 전역 CSS를 주입하여
일관된 디자인 언어를 제공한다.
"""

import streamlit as st

# ============================================================
# 색상 팔레트
# 초보자 친화적인 부드러운 색상 체계. WCAG AA 대비율을 최대한 준수한다.
# ============================================================
THEME = {
    # 주요 인터랙션 색상
    "primary": "#4A90D9",       # 파란색: 주요 버튼, 링크, 강조
    "secondary": "#7C8DB5",     # 중간 파란-회색: 보조 요소
    # 배경 및 표면
    "background": "#FAFBFC",    # 거의 흰색 배경: 눈 피로 감소
    "surface": "#FFFFFF",       # 순수 흰색: 카드, 패널
    # 텍스트
    "text_primary": "#2D3748",  # 짙은 회색: 주요 텍스트 (흰 배경에서 WCAG AA 통과)
    "text_secondary": "#718096",  # 중간 회색: 보조 텍스트, 힌트
    # 상태 색상
    "success": "#48BB78",       # 초록: 정답, 완료, 통과
    "error": "#F56565",         # 빨강: 오류, 실패
    "warning": "#ED8936",       # 주황: 경고, 중급 난이도
    "info": "#4299E1",          # 밝은 파란: 정보, 안내
    # 난이도 색상 (DIFFICULTY_LABELS와 동기화)
    "difficulty_basic": "#48BB78",        # 초록: 기초
    "difficulty_intermediate": "#ED8936",  # 주황: 중급
    "difficulty_advanced": "#F56565",     # 빨강: 심화
    # 코드 에디터 (VS Code Dark 테마 기반)
    "editor_bg": "#1E1E1E",     # 짙은 배경: 장시간 코딩 시 눈 편안
    "editor_text": "#D4D4D4",   # 밝은 회색 텍스트
}

# ============================================================
# 난이도 레이블 설정
# 색상 + 텍스트 + 아이콘(★) 세 가지 채널로 난이도를 표현한다.
# 색맹 사용자를 위해 색상만이 아닌 텍스트+아이콘을 병용한다.
# ============================================================
DIFFICULTY_LABELS = {
    "basic": {
        "label": "기초",
        "icon": "★",
        "color": "#48BB78",
    },
    "intermediate": {
        "label": "중급",
        "icon": "★★",
        "color": "#ED8936",
    },
    "advanced": {
        "label": "심화",
        "icon": "★★★",
        "color": "#F56565",
    },
}


def apply_theme() -> None:
    """앱 전체에 커스텀 CSS를 주입한다.

    st.markdown unsafe_allow_html=True를 사용하여
    Google Fonts Noto Sans KR 로드 + 전역 스타일을 설정한다.

    주입 항목:
        - Noto Sans KR 폰트 (Google Fonts CDN)
        - 난이도 배지 스타일 (.badge-basic, .badge-intermediate, .badge-advanced)
        - 코드 에디터 영역 스타일
        - 진행도 바 스타일
        - 버튼 스타일 (실행=파랑, 제출=초록, 초기화=회색)
        - 모바일 반응형 (@media max-width: 768px)
        - 폰트 크기 조절 (.font-size-small, .font-size-large)

    Note:
        - session_state["font_size"]가 "small"이면 .font-size-small 클래스 활성화
        - session_state["font_size"]가 "large"이면 .font-size-large 클래스 활성화
        - 기본값은 "medium" (변경 없음)
    """
    # 현재 세션의 폰트 크기 설정 읽기
    # 초기값이 없으면 "medium"으로 설정
    if "font_size" not in st.session_state:
        st.session_state["font_size"] = "medium"

    font_size = st.session_state.get("font_size", "medium")

    # 폰트 크기에 따른 CSS 변수 결정
    # 기초: 14px, 중간: 16px, 크게: 18px
    font_size_map = {
        "small": "14px",
        "medium": "16px",
        "large": "18px",
    }
    base_font_size = font_size_map.get(font_size, "16px")

    # CSS 전체를 f-string으로 구성하여 동적 값 삽입
    css = f"""
    <style>
    /* ===== Google Fonts: Noto Sans KR 로드 =====
       한국어 웹폰트. subset=korean으로 필요한 글자만 로드하여 성능 최적화 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    /* ===== 전역 폰트 설정 ===== */
    html, body, [class*="css"] {{
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', sans-serif;
        font-size: {base_font_size};
        color: {THEME['text_primary']};
        background-color: {THEME['background']};
    }}

    /* ===== 메인 컨텐츠 영역 여백 ===== */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }}

    /* ===== 난이도 배지 스타일 =====
       색맹 접근성을 위해 색상 + 텍스트 + 아이콘 세 가지 채널 사용 */
    .difficulty-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.82em;
        font-weight: 700;
        line-height: 1.4;
        letter-spacing: 0.02em;
    }}

    /* 기초: 초록 배지 */
    .badge-basic {{
        background-color: #ECFDF5;
        color: {DIFFICULTY_LABELS['basic']['color']};
        border: 1px solid {DIFFICULTY_LABELS['basic']['color']};
    }}

    /* 중급: 주황 배지 */
    .badge-intermediate {{
        background-color: #FFF7ED;
        color: {DIFFICULTY_LABELS['intermediate']['color']};
        border: 1px solid {DIFFICULTY_LABELS['intermediate']['color']};
    }}

    /* 심화: 빨강 배지 */
    .badge-advanced {{
        background-color: #FFF5F5;
        color: {DIFFICULTY_LABELS['advanced']['color']};
        border: 1px solid {DIFFICULTY_LABELS['advanced']['color']};
    }}

    /* ===== 코드 에디터 영역 스타일 =====
       streamlit-code-editor 컨테이너에 적용되는 래퍼 스타일 */
    .code-editor-wrapper {{
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        overflow: hidden;
        margin: 0.75rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }}

    /* 코드 에디터 내부 폰트: 등폭 폰트로 코드 가독성 확보 */
    .ace_editor {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas',
                     'Monaco', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }}

    /* st.text_area 기반 모바일 에디터 스타일 */
    textarea[data-testid="stTextArea"] {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 13px;
        background-color: {THEME['editor_bg']};
        color: {THEME['editor_text']};
        border-radius: 6px;
        padding: 12px;
        min-height: 200px;
    }}

    /* ===== 진행도 바 스타일 ===== */
    .progress-label {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
        font-size: 0.85em;
        color: {THEME['text_secondary']};
    }}

    /* Streamlit 기본 진행도 바 커스터마이징 */
    .stProgress > div > div > div > div {{
        background-color: {THEME['primary']};
        border-radius: 4px;
        transition: width 0.4s ease;
    }}

    .stProgress > div > div > div {{
        background-color: #E2E8F0;
        border-radius: 4px;
        height: 10px;
    }}

    /* ===== 버튼 스타일 =====
       역할별 색상 구분: 실행=파랑, 제출=초록, 초기화=회색 */

    /* 실행 버튼 (data-testid로 특정 버튼을 정확히 타겟하기 어려워
       클래스 기반으로 래퍼에서 관리) */
    .btn-run > button {{
        background-color: {THEME['primary']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }}
    .btn-run > button:hover {{
        background-color: #3182CE !important;
        box-shadow: 0 2px 8px rgba(66, 153, 225, 0.4) !important;
        transform: translateY(-1px) !important;
    }}

    /* 제출 버튼 */
    .btn-submit > button {{
        background-color: {THEME['success']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }}
    .btn-submit > button:hover {{
        background-color: #38A169 !important;
        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.4) !important;
        transform: translateY(-1px) !important;
    }}

    /* 초기화 버튼 */
    .btn-reset > button {{
        background-color: #718096 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }}
    .btn-reset > button:hover {{
        background-color: #4A5568 !important;
        transform: translateY(-1px) !important;
    }}

    /* ===== 개념 카드 스타일 ===== */
    .concept-card {{
        background-color: {THEME['surface']};
        border-left: 4px solid {THEME['primary']};
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }}

    /* 핵심 포인트 리스트 스타일 */
    .key-point {{
        background-color: #EBF8FF;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        font-size: 0.9em;
        color: #2B6CB0;
    }}

    /* ===== 힌트 패널 스타일 ===== */
    .hint-panel {{
        background-color: #FFFFF0;
        border: 1px solid #F6E05E;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }}

    /* 보상 프레이밍 배너: 힌트 미사용 시 보너스 안내 */
    .hint-reward-banner {{
        background: linear-gradient(135deg, #48BB78, #38A169);
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.88em;
        font-weight: 600;
        margin-bottom: 0.75rem;
        text-align: center;
    }}

    /* ===== 채점 결과 스타일 ===== */
    .grade-pass {{
        background-color: #F0FFF4;
        border: 2px solid {THEME['success']};
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
    }}

    .grade-partial {{
        background-color: #FFFAF0;
        border: 2px solid {THEME['warning']};
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
    }}

    .grade-fail {{
        background-color: #FFF5F5;
        border: 2px solid {THEME['error']};
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
    }}

    /* ===== 에러 메시지 스타일: 겁주지 않는 디자인 =====
       빨간색 대신 차분한 노란-주황 계열로 불안감 최소화 */
    .error-friendly {{
        background-color: #FFFBEB;
        border: 1px solid #F6AD55;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
    }}

    .error-friendly .error-title {{
        font-weight: 700;
        color: #C05621;
        font-size: 1em;
        margin-bottom: 0.5rem;
    }}

    .error-friendly .error-checklist {{
        font-size: 0.88em;
        color: #744210;
        margin-top: 0.5rem;
    }}

    /* ===== 온보딩 스타일 ===== */
    .onboarding-container {{
        max-width: 640px;
        margin: 3rem auto;
        text-align: center;
        padding: 2rem;
    }}

    .onboarding-step-indicator {{
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 1.5rem;
    }}

    .step-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #CBD5E0;
    }}

    .step-dot.active {{
        background-color: {THEME['primary']};
        transform: scale(1.3);
    }}

    /* ===== 문제 목록 네비게이션 ===== */
    .problem-nav-item {{
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.2rem 0;
        cursor: pointer;
        transition: background-color 0.15s ease;
        font-size: 0.9em;
    }}

    .problem-nav-item:hover {{
        background-color: #EBF8FF;
    }}

    .problem-nav-item.current {{
        background-color: #BEE3F8;
        font-weight: 600;
        color: {THEME['primary']};
    }}

    .problem-nav-item.completed {{
        color: {THEME['success']};
    }}

    /* ===== 반응형 레이아웃 =====
       모바일 (max-width: 768px)에서 레이아웃 조정 */
    @media (max-width: 768px) {{
        /* 메인 컨테이너 패딩 줄이기 */
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        /* 버튼을 전체 너비로 확장 */
        .btn-run, .btn-submit, .btn-reset {{
            width: 100%;
        }}
        .btn-run > button,
        .btn-submit > button,
        .btn-reset > button {{
            width: 100% !important;
        }}

        /* 코드 에디터 높이 축소 */
        .ace_editor {{
            min-height: 200px !important;
        }}

        /* 사이드바 숨기기 (모바일에서 기본 접힘) */
        .css-1d391kg {{
            padding: 0.5rem;
        }}

        /* 온보딩 컨테이너 여백 조정 */
        .onboarding-container {{
            margin: 1rem auto;
            padding: 1rem;
        }}

        /* 폰트 크기 약간 줄이기 */
        html, body, [class*="css"] {{
            font-size: 14px;
        }}
    }}

    /* ===== 폰트 크기 조절 유틸리티 클래스 ===== */
    .font-size-small {{
        font-size: 14px !important;
    }}

    .font-size-large {{
        font-size: 18px !important;
    }}

    /* ===== 기타 Streamlit 기본 스타일 오버라이드 ===== */
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.95em;
        font-weight: 500;
        padding: 0.5rem 1.25rem;
        border-radius: 6px 6px 0 0;
    }}

    /* 헤더 스타일 */
    h1, h2, h3 {{
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 700;
        color: {THEME['text_primary']};
        line-height: 1.4;
    }}

    /* 구분선 */
    hr {{
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 1.5rem 0;
    }}

    /* 성공/에러 메시지 박스 */
    .stSuccess {{
        border-radius: 8px;
    }}

    .stError {{
        border-radius: 8px;
    }}

    /* 스크롤바 커스터마이징 */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}

    ::-webkit-scrollbar-track {{
        background: #F7FAFC;
    }}

    ::-webkit-scrollbar-thumb {{
        background: #CBD5E0;
        border-radius: 3px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: #A0AEC0;
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def set_font_size(size: str) -> None:
    """폰트 크기 설정을 세션 상태에 저장하고 테마를 재적용한다.

    Args:
        size: 폰트 크기 설정값. "small" | "medium" | "large" 중 하나.
            - "small": 14px (고밀도 화면, 작은 기기)
            - "medium": 16px (기본값)
            - "large": 18px (시력 약한 사용자, 큰 모니터)

    Note:
        변경 후 apply_theme()를 다시 호출해야 CSS에 반영된다.
        일반적으로 이 함수 호출 후 st.rerun()을 실행한다.
    """
    if size not in ("small", "medium", "large"):
        # 잘못된 값은 중간 크기로 fallback
        size = "medium"

    st.session_state["font_size"] = size
