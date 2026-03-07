"""챕터 7: 예외 처리 학습 페이지.

try/except, 예외 종류, else, finally, raise, 사용자 정의 예외 등
파이썬 예외 처리의 핵심 개념을 배우고 15개 문제로 연습한다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 7 - 예외 처리",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=7)

with content:
    renderer = ChapterRenderer(chapter_id=7)
    renderer.render()
