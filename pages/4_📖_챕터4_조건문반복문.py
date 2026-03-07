"""챕터 4: 조건문/반복문 학습 페이지.

if/elif/else, for, while, enumerate, 리스트 컴프리헨션 등
제어 흐름을 배우고 15개 문제로 연습한다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_sidebar

st.set_page_config(
    page_title="챕터 4 - 조건문/반복문",
    page_icon="📖",
    layout="wide",
)

apply_theme()
render_chat_sidebar(chapter_id=4)

renderer = ChapterRenderer(chapter_id=4)
renderer.render()
