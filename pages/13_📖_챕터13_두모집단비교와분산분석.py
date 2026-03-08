"""챕터 13: 두 모집단 비교와 분산분석 학습 페이지.

독립/대응표본 t검정, 일원배치/이원배치 분산분석(ANOVA)을 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 13 - 두 모집단 비교와 분산분석",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=13)

with content:
    renderer = ChapterRenderer(chapter_id=13)
    renderer.render()
