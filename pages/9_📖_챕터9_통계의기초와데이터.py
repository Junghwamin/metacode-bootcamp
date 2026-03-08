"""챕터 9: 통계의 기초와 데이터 학습 페이지.

중심경향 측도, 산포도 측도, 상관분석 등 기술통계의 기본을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 9 - 통계의 기초와 데이터",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=9)

with content:
    renderer = ChapterRenderer(chapter_id=9)
    renderer.render()
