"""앱 테마 및 스타일 정의.

Noto Sans KR + Inter 폰트, Claymorphism + Minimal Swiss 디자인 시스템,
교육/테크 컬러 팔레트 적용. WCAG AA 대비율 준수.
"""

import streamlit as st

# ============================================================
# 색상 팔레트
# UI/UX Pro Max - Education/Tech 팔레트
# Claymorphism(교육적, 접근 친화적) + Minimal Swiss(깔끔한 대시보드) 결합
# ============================================================
THEME = {
    # 주요 인터랙션 색상
    "primary": "#4A90D9",       # Trust Blue: 주요 버튼, 링크, 강조
    "secondary": "#6C63FF",     # Vibrant Purple: 보조 강조, 현대적 느낌
    "accent": "#FF6B6B",        # Coral: CTA 버튼, 따뜻하고 초대하는 느낌
    # 배경 및 표면
    "background": "#F7F8FC",    # Soft Lavender Grey: 눈 피로 감소
    "surface": "#FFFFFF",       # 순수 흰색: 카드, 패널
    # 텍스트
    "text_primary": "#2D3436",  # Near Black: 주요 텍스트 (WCAG AA 통과)
    "text_secondary": "#636E72",  # Cool Grey: 보조 텍스트, 힌트
    # 상태 색상
    "success": "#00C48C",       # Fresh Green: 정답, 완료, 통과
    "error": "#FF6B6B",         # Coral Red: 오류, 실패
    "warning": "#FFB946",       # Warm Amber: 경고, 중급 난이도
    "info": "#4A90D9",          # Trust Blue: 정보, 안내
    # 난이도 색상 (DIFFICULTY_LABELS와 동기화)
    "difficulty_basic": "#00C48C",        # Fresh Green: 기초
    "difficulty_intermediate": "#FFB946",  # Warm Amber: 중급
    "difficulty_advanced": "#FF6B6B",     # Coral: 심화
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
        "color": "#00C48C",
    },
    "intermediate": {
        "label": "중급",
        "icon": "★★",
        "color": "#FFB946",
    },
    "advanced": {
        "label": "심화",
        "icon": "★★★",
        "color": "#FF6B6B",
    },
}


def apply_theme() -> None:
    """앱 전체에 커스텀 CSS를 주입한다.

    Claymorphism + Minimal Swiss 디자인 시스템 적용.
    Google Fonts Noto Sans KR + Inter 로드 + 전역 스타일 설정.

    주입 항목:
        - Noto Sans KR + Inter 폰트 (Google Fonts CDN)
        - 카드 호버 리프트 효과 (translateY(-2px) + 섀도우)
        - 부드러운 섀도우 (harsh border 제거)
        - CTA 그라디언트 버튼 스타일
        - 개선된 탭 스타일
        - 사이드바 글래스모피즘
        - 코드 에디터 컨테이너 개선
        - 채팅 메시지 스타일 (AI 튜터 페이지용)
        - 8px 그리드 시스템 기반 간격
        - 모바일 반응형 (@media max-width: 768px)

    Note:
        - session_state["font_size"]가 "small"이면 14px
        - session_state["font_size"]가 "large"이면 18px
        - 기본값은 "medium" (16px)
    """
    # 현재 세션의 폰트 크기 설정 읽기
    if "font_size" not in st.session_state:
        st.session_state["font_size"] = "medium"

    font_size = st.session_state.get("font_size", "medium")

    # 폰트 크기에 따른 CSS 변수 결정
    font_size_map = {
        "small": "14px",
        "medium": "16px",
        "large": "18px",
    }
    base_font_size = font_size_map.get(font_size, "16px")

    css = f"""
    <style>
    /* ===== Google Fonts: Noto Sans KR + Inter 로드 =====
       Noto Sans KR: 한국어 웹폰트
       Inter: UI 요소용 현대적 산세리프 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    /* ===== CSS 변수: 8px 그리드 시스템 =====
       모든 간격은 8의 배수로 통일하여 시각적 일관성 확보 */
    :root {{
        --color-primary: {THEME['primary']};
        --color-secondary: {THEME['secondary']};
        --color-accent: {THEME['accent']};
        --color-success: {THEME['success']};
        --color-warning: {THEME['warning']};
        --color-error: {THEME['error']};
        --color-bg: {THEME['background']};
        --color-surface: {THEME['surface']};
        --color-text-primary: {THEME['text_primary']};
        --color-text-secondary: {THEME['text_secondary']};

        /* 8px 그리드 */
        --space-1: 8px;
        --space-2: 16px;
        --space-3: 24px;
        --space-4: 32px;
        --space-5: 40px;
        --space-6: 48px;

        /* 보더 반지름 */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-badge: 20px;

        /* 섀도우 - Claymorphism 스타일 */
        --shadow-card: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
        --shadow-card-hover: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
        --shadow-elevated: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);

        /* 트랜지션 */
        --transition-fast: all 0.2s ease;
        --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* ===== 전역 폰트 설정 ===== */
    html, body, [class*="css"] {{
        font-family: 'Noto Sans KR', 'Inter', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', sans-serif;
        font-size: {base_font_size};
        color: var(--color-text-primary);
        background-color: var(--color-bg);
    }}

    /* ===== 메인 컨텐츠 영역 여백 ===== */
    .main .block-container {{
        padding-top: var(--space-3);
        padding-bottom: var(--space-6);
        max-width: 900px;
    }}

    /* ===== 헤더 스타일 ===== */
    h1, h2, h3, h4 {{
        font-family: 'Noto Sans KR', 'Inter', sans-serif;
        font-weight: 700;
        color: var(--color-text-primary);
        line-height: 1.4;
    }}

    h1 {{
        font-size: 1.875rem;
        letter-spacing: -0.025em;
    }}

    h2 {{
        font-size: 1.5rem;
        letter-spacing: -0.015em;
    }}

    /* ===== 사이드바 글래스모피즘 =====
       반투명 배경 + 백드롭 블러로 현대적인 느낌 */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.5) !important;
    }}

    [data-testid="stSidebar"] > div {{
        background: transparent !important;
    }}

    /* ===== 난이도 배지 스타일 =====
       색맹 접근성을 위해 색상 + 텍스트 + 아이콘 세 가지 채널 사용 */
    .difficulty-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 12px;
        border-radius: var(--radius-badge);
        font-size: 0.78em;
        font-weight: 700;
        line-height: 1.4;
        letter-spacing: 0.03em;
        font-family: 'Inter', sans-serif;
    }}

    /* 기초: Fresh Green 배지 */
    .badge-basic {{
        background-color: rgba(0, 196, 140, 0.12);
        color: {DIFFICULTY_LABELS['basic']['color']};
        border: 1.5px solid rgba(0, 196, 140, 0.35);
    }}

    /* 중급: Warm Amber 배지 */
    .badge-intermediate {{
        background-color: rgba(255, 185, 70, 0.12);
        color: {DIFFICULTY_LABELS['intermediate']['color']};
        border: 1.5px solid rgba(255, 185, 70, 0.35);
    }}

    /* 심화: Coral 배지 */
    .badge-advanced {{
        background-color: rgba(255, 107, 107, 0.12);
        color: {DIFFICULTY_LABELS['advanced']['color']};
        border: 1.5px solid rgba(255, 107, 107, 0.35);
    }}

    /* ===== 공통 카드 스타일 =====
       Claymorphism: 부드러운 섀도우 + 둥근 모서리 + 호버 리프트 */
    .card {{
        background: var(--color-surface);
        border-radius: var(--radius-md);
        padding: var(--space-2);
        border: 1px solid rgba(0, 0, 0, 0.06);
        box-shadow: var(--shadow-card);
        transition: var(--transition-fast);
    }}

    .card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-card-hover);
    }}

    /* ===== 코드 에디터 영역 스타일 ===== */
    .code-editor-wrapper {{
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: var(--radius-md);
        overflow: hidden;
        margin: var(--space-1) 0;
        box-shadow: var(--shadow-card);
        transition: var(--transition-fast);
    }}

    .code-editor-wrapper:focus-within {{
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.15), var(--shadow-card);
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
        border-radius: var(--radius-sm);
        padding: var(--space-1) 12px;
        min-height: 200px;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}

    /* ===== 진행도 바 스타일 ===== */
    .progress-label {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
        font-size: 0.85em;
        color: var(--color-text-secondary);
    }}

    /* Streamlit 기본 진행도 바 커스터마이징 */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
        border-radius: 4px;
        transition: width 0.4s ease;
    }}

    .stProgress > div > div > div {{
        background-color: rgba(0, 0, 0, 0.08);
        border-radius: 4px;
        height: 8px;
    }}

    /* ===== 버튼 스타일 =====
       역할별 색상 구분: CTA=그라디언트, 실행=파랑, 제출=그린, 초기화=회색 */

    /* 실행 버튼 */
    .btn-run > button {{
        background: linear-gradient(135deg, {THEME['primary']}, #357ABD) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        padding: 0.5rem 1.5rem !important;
        transition: var(--transition-fast) !important;
        box-shadow: 0 2px 6px rgba(74, 144, 217, 0.3) !important;
    }}
    .btn-run > button:hover {{
        background: linear-gradient(135deg, #357ABD, #2868A8) !important;
        box-shadow: 0 4px 12px rgba(74, 144, 217, 0.45) !important;
        transform: translateY(-1px) !important;
    }}

    /* 제출 버튼 */
    .btn-submit > button {{
        background: linear-gradient(135deg, {THEME['success']}, #00A37A) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        padding: 0.5rem 1.5rem !important;
        transition: var(--transition-fast) !important;
        box-shadow: 0 2px 6px rgba(0, 196, 140, 0.3) !important;
    }}
    .btn-submit > button:hover {{
        background: linear-gradient(135deg, #00A37A, #008564) !important;
        box-shadow: 0 4px 12px rgba(0, 196, 140, 0.45) !important;
        transform: translateY(-1px) !important;
    }}

    /* 초기화 버튼 */
    .btn-reset > button {{
        background: linear-gradient(135deg, #636E72, #4A555A) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        padding: 0.5rem 1.5rem !important;
        transition: var(--transition-fast) !important;
    }}
    .btn-reset > button:hover {{
        background: linear-gradient(135deg, #4A555A, #363F42) !important;
        transform: translateY(-1px) !important;
    }}

    /* CTA 버튼 (primary Streamlit 버튼) */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {THEME['accent']}, #E85555) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.35) !important;
        transition: var(--transition-fast) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 6px 16px rgba(255, 107, 107, 0.45) !important;
        transform: translateY(-1px) !important;
    }}

    /* ===== 개념 카드 스타일 ===== */
    .concept-card {{
        background: var(--color-surface);
        border-left: 4px solid var(--color-primary);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        padding: var(--space-2) 20px;
        margin: var(--space-1) 0;
        box-shadow: var(--shadow-card);
        transition: var(--transition-fast);
    }}

    .concept-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-card-hover);
    }}

    /* 핵심 포인트 리스트 스타일 */
    .key-point {{
        background: rgba(74, 144, 217, 0.08);
        border-radius: var(--radius-sm);
        padding: 6px 12px;
        margin: 4px 0;
        font-size: 0.9em;
        color: #2563EB;
        border-left: 3px solid var(--color-primary);
    }}

    /* ===== 힌트 패널 스타일 ===== */
    .hint-panel {{
        background: rgba(255, 185, 70, 0.08);
        border: 1.5px solid rgba(255, 185, 70, 0.35);
        border-radius: var(--radius-md);
        padding: var(--space-2);
        margin-top: var(--space-2);
    }}

    /* 보상 프레이밍 배너: 힌트 미사용 시 보너스 안내 */
    .hint-reward-banner {{
        background: linear-gradient(135deg, {THEME['success']}, #00A37A);
        color: white;
        border-radius: var(--radius-sm);
        padding: var(--space-1) var(--space-2);
        font-size: 0.88em;
        font-weight: 600;
        margin-bottom: var(--space-1);
        text-align: center;
    }}

    /* ===== 채점 결과 스타일 ===== */
    .grade-pass {{
        background: rgba(0, 196, 140, 0.06);
        border: 2px solid {THEME['success']};
        border-radius: var(--radius-md);
        padding: var(--space-2);
        margin: var(--space-1) 0;
        box-shadow: var(--shadow-sm);
    }}

    .grade-partial {{
        background: rgba(255, 185, 70, 0.06);
        border: 2px solid {THEME['warning']};
        border-radius: var(--radius-md);
        padding: var(--space-2);
        margin: var(--space-1) 0;
        box-shadow: var(--shadow-sm);
    }}

    .grade-fail {{
        background: rgba(255, 107, 107, 0.06);
        border: 2px solid {THEME['error']};
        border-radius: var(--radius-md);
        padding: var(--space-2);
        margin: var(--space-1) 0;
        box-shadow: var(--shadow-sm);
    }}

    /* ===== 에러 메시지 스타일: 겁주지 않는 디자인 =====
       빨간색 대신 차분한 Warm Amber 계열로 불안감 최소화 */
    .error-friendly {{
        background: rgba(255, 185, 70, 0.08);
        border: 1.5px solid rgba(255, 185, 70, 0.4);
        border-radius: var(--radius-md);
        padding: var(--space-2) 20px;
        margin: var(--space-1) 0;
    }}

    .error-friendly .error-title {{
        font-weight: 700;
        color: #B45309;
        font-size: 1em;
        margin-bottom: var(--space-1);
    }}

    .error-friendly .error-checklist {{
        font-size: 0.88em;
        color: #78350F;
        margin-top: var(--space-1);
    }}

    /* ===== 온보딩 스타일 ===== */
    .onboarding-container {{
        max-width: 640px;
        margin: var(--space-5) auto;
        text-align: center;
        padding: var(--space-4);
        background: var(--color-surface);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-elevated);
        border: 1px solid rgba(0, 0, 0, 0.06);
    }}

    .onboarding-step-indicator {{
        display: flex;
        justify-content: center;
        gap: var(--space-1);
        margin-bottom: var(--space-3);
    }}

    .step-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: rgba(0, 0, 0, 0.12);
        transition: var(--transition-fast);
    }}

    .step-dot.active {{
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        transform: scale(1.4);
    }}

    /* ===== 문제 목록 네비게이션 ===== */
    .problem-nav-item {{
        padding: var(--space-1) 12px;
        border-radius: var(--radius-sm);
        margin: 3px 0;
        cursor: pointer;
        transition: var(--transition-fast);
        font-size: 0.9em;
    }}

    .problem-nav-item:hover {{
        background: rgba(74, 144, 217, 0.08);
    }}

    .problem-nav-item.current {{
        background: rgba(74, 144, 217, 0.15);
        font-weight: 600;
        color: var(--color-primary);
    }}

    .problem-nav-item.completed {{
        color: {THEME['success']};
    }}

    /* ===== 메트릭 카드 커스텀 스타일 ===== */
    .metric-card {{
        background: var(--color-surface);
        border-radius: var(--radius-md);
        padding: var(--space-2) var(--space-3);
        box-shadow: var(--shadow-card);
        border: 1px solid rgba(0, 0, 0, 0.06);
        text-align: center;
        transition: var(--transition-fast);
    }}

    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-card-hover);
    }}

    .metric-card .metric-value {{
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--color-primary);
        line-height: 1.2;
        margin-bottom: 4px;
    }}

    .metric-card .metric-label {{
        font-size: 0.82em;
        font-weight: 500;
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    /* ===== AI 튜터 채팅 메시지 스타일 ===== */
    .chat-message-user {{
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        color: white;
        border-radius: var(--radius-md) var(--radius-md) 4px var(--radius-md);
        padding: 10px 16px;
        margin: var(--space-1) 0 var(--space-1) var(--space-6);
        font-size: 0.92em;
        box-shadow: var(--shadow-sm);
    }}

    .chat-message-ai {{
        background: var(--color-surface);
        color: var(--color-text-primary);
        border-radius: var(--radius-md) var(--radius-md) var(--radius-md) 4px;
        padding: 10px 16px;
        margin: var(--space-1) var(--space-6) var(--space-1) 0;
        font-size: 0.92em;
        box-shadow: var(--shadow-card);
        border: 1px solid rgba(0, 0, 0, 0.06);
    }}

    /* ===== 탭 스타일 개선 ===== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: rgba(0, 0, 0, 0.04);
        border-radius: var(--radius-sm);
        padding: 4px;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: 'Noto Sans KR', 'Inter', sans-serif;
        font-size: 0.92em;
        font-weight: 500;
        padding: 6px 20px;
        border-radius: 6px;
        color: var(--color-text-secondary);
        transition: var(--transition-fast);
    }}

    .stTabs [aria-selected="true"] {{
        background: var(--color-surface) !important;
        color: var(--color-primary) !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-sm) !important;
    }}

    /* ===== 구분선 ===== */
    hr {{
        border: none;
        border-top: 1px solid rgba(0, 0, 0, 0.08);
        margin: var(--space-3) 0;
    }}

    /* ===== Streamlit 기본 컴포넌트 스타일 오버라이드 ===== */
    .stSuccess {{
        border-radius: var(--radius-md);
        background: rgba(0, 196, 140, 0.06) !important;
        border: 1px solid rgba(0, 196, 140, 0.3) !important;
    }}

    .stError {{
        border-radius: var(--radius-md);
        background: rgba(255, 107, 107, 0.06) !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
    }}

    .stInfo {{
        border-radius: var(--radius-md);
        background: rgba(74, 144, 217, 0.06) !important;
        border: 1px solid rgba(74, 144, 217, 0.3) !important;
    }}

    .stWarning {{
        border-radius: var(--radius-md);
        background: rgba(255, 185, 70, 0.06) !important;
        border: 1px solid rgba(255, 185, 70, 0.3) !important;
    }}

    /* ===== 스크롤바 커스터마이징 ===== */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--color-bg);
    }}

    ::-webkit-scrollbar-thumb {{
        background: rgba(0, 0, 0, 0.15);
        border-radius: 3px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(0, 0, 0, 0.25);
    }}

    /* ===== 반응형 레이아웃 =====
       모바일 (max-width: 768px)에서 레이아웃 조정 */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: var(--space-2);
            padding-right: var(--space-2);
        }}

        .btn-run, .btn-submit, .btn-reset {{
            width: 100%;
        }}
        .btn-run > button,
        .btn-submit > button,
        .btn-reset > button {{
            width: 100% !important;
        }}

        .ace_editor {{
            min-height: 200px !important;
        }}

        .onboarding-container {{
            margin: var(--space-2) auto;
            padding: var(--space-2);
        }}

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
