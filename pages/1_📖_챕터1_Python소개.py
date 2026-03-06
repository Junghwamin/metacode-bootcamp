"""챕터 1: Python 소개 학습 페이지.

주석, 변수, print(), input() 등 파이썬의 기본 문법을 배우고
15개 문제로 연습한다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme

st.set_page_config(
    page_title="챕터 1 - Python 소개",
    page_icon="📖",
    layout="wide",
)

apply_theme()

renderer = ChapterRenderer(chapter_id=1)
renderer.render()
