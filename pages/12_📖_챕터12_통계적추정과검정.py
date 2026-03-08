"""챕터 12: 통계적 추정과 검정 학습 페이지.

점추정, 구간추정, 가설검정, p-value 해석을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 12 - 통계적 추정과 검정",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=12)

with content:
    renderer = ChapterRenderer(chapter_id=12)
    renderer.render()
