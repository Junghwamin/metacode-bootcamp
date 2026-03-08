"""챕터 14: 회귀분석 학습 페이지.

단순 선형 회귀분석의 원리, 최소제곱법, R², 잔차분석을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 14 - 회귀분석",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=14)

with content:
    renderer = ChapterRenderer(chapter_id=14)
    renderer.render()
