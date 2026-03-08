"""챕터 17: 마케팅 데이터 분석 실전 학습 페이지.

기여분석, 전환윈도우, CPC, ROAS 등 마케팅 핵심 분석 기법을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 17 - 마케팅 데이터 분석 실전",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=17)

with content:
    renderer = ChapterRenderer(chapter_id=17)
    renderer.render()
