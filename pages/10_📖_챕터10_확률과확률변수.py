"""챕터 10: 확률과 확률변수 학습 페이지.

확률의 기본 개념, 조건부확률, 베이즈정리, 확률변수, 기대값을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 10 - 확률과 확률변수",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=10)

with content:
    renderer = ChapterRenderer(chapter_id=10)
    renderer.render()
