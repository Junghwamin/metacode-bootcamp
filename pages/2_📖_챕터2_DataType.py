"""챕터 2: DataType 학습 페이지.

Number, 연산자, String, Boolean 등 파이썬의 기본 자료형을 배우고
15개 문제로 연습한다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_sidebar

st.set_page_config(
    page_title="챕터 2 - DataType",
    page_icon="📖",
    layout="wide",
)

apply_theme()
render_chat_sidebar(chapter_id=2)

renderer = ChapterRenderer(chapter_id=2)
renderer.render()
