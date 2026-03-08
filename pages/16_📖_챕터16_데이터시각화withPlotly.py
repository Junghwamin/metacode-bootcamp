"""챕터 16: 데이터 시각화 with Plotly 학습 페이지.

Plotly를 활용한 인터랙티브 차트 (bar, line, histogram, pie, scatter)를 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 16 - 데이터 시각화 with Plotly",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=16)

with content:
    renderer = ChapterRenderer(chapter_id=16)
    renderer.render()
