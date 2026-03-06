"""챕터 3: 자료형 학습 페이지.

List, Tuple, Set, Dictionary 등 파이썬의 자료형을 배우고
15개 문제로 연습한다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme

st.set_page_config(
    page_title="챕터 3 - 자료형",
    page_icon="📖",
    layout="wide",
)

apply_theme()

renderer = ChapterRenderer(chapter_id=3)
renderer.render()
