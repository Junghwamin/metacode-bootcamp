"""챕터 5: 함수와 클래스 학습 페이지.

def, return, 매개변수, 클래스, 상속 등 파이썬 함수/클래스의
핵심 개념을 배우고 15개 문제로 연습한다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme

st.set_page_config(
    page_title="챕터 5 - 함수와 클래스",
    page_icon="📖",
    layout="wide",
)

apply_theme()

renderer = ChapterRenderer(chapter_id=5)
renderer.render()
