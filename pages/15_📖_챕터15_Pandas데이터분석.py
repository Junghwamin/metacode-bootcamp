"""챕터 15: Pandas 데이터 분석 학습 페이지.

DataFrame, 인덱싱, 필터링, groupby, merge, pivot 등 Pandas 핵심 기능을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 15 - Pandas 데이터 분석",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=15)

with content:
    renderer = ChapterRenderer(chapter_id=15)
    renderer.render()
