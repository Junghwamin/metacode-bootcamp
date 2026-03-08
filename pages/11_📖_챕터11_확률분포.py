"""챕터 11: 확률분포 학습 페이지.

이항분포, 포아송분포, 정규분포, 중심극한정리, 표본분포를 배운다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 11 - 확률분포",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=11)

with content:
    renderer = ChapterRenderer(chapter_id=11)
    renderer.render()
