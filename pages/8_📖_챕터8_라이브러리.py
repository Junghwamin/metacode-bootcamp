"""챕터 8: 라이브러리 학습 페이지.

NumPy(수치 계산)와 Pandas(데이터 분석) 라이브러리의
핵심 기능을 배우고 15개 문제로 연습한다.
이 챕터에서는 numpy와 pandas 모듈 import가 허용된다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme

st.set_page_config(
    page_title="챕터 8 - NumPy와 Pandas",
    page_icon="📖",
    layout="wide",
)

apply_theme()

renderer = ChapterRenderer(chapter_id=8)
renderer.render()
