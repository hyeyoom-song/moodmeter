# demos/_template/app.py

import streamlit as st

# ← 여기에 위에서 제공한 감정 배열, 메뉴, 페이지 구분 등 코드를 붙여 넣거나,
#    기존 메뉴가 있으면 그 내부에 무드미터 감정기록 페이지 부분을 추가하세요

# (예시)
moodmeter = [...]  # 16개 감정 및 색상 배열

menu = st.sidebar.radio(
    "메뉴를 선택하세요",
    ("첫 페이지", "무드미터 감정기록")
)

if menu == "첫 페이지":
    # 기존 메인화면 코드
    ...

elif menu == "무드미터 감정기록":
    # 위의 예시에서 제공된 감정 선택 UI 코드
    ...
