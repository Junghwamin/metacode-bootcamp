"""챕터 6: 파일 다루기 학습 페이지.

open, read, write, with문, 파일 모드(r/w/a) 등
파이썬 파일 입출력의 핵심 개념을 배우고 15개 문제로 연습한다.
가상 파일시스템(virtual_fs)을 사용하여 실제 파일 없이도 연습 가능하다.
"""

import streamlit as st
from ui.chapter_renderer import ChapterRenderer
from ui.theme import apply_theme
from ui.chat_sidebar import render_chat_panel

st.set_page_config(
    page_title="챕터 6 - 파일 다루기",
    page_icon="📖",
    layout="wide",
)

apply_theme()
content = render_chat_panel(chapter_id=6)

with content:
    renderer = ChapterRenderer(chapter_id=6)
    renderer.render()
