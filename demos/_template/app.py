import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import random
import time
import io

# 학생 목록
STUDENT_LIST = ["김철수", "이영희", "박민준", "최다은", "정하늘"]

# 16가지 감정 정의 (이름, 이모지, 색상)
EMOTIONS = [
    ("행복", "😊", "#FFD93D"),   ("즐거움", "😄", "#FFB84C"),
    ("설렘", "😍", "#FF6D60"),   ("평온", "😌", "#A7FFE4"),
    ("감사", "🙏", "#98D8AA"),   ("자신감", "😎", "#7A9D54"),
    ("힘남", "💪", "#40A2E3"),   ("용기", "🧗‍♂️", "#38E54D"),
    ("슬픔", "😢", "#72A0C1"),   ("피곤", "🥱", "#625772"),
    ("화남", "😡", "#FF8787"),   ("두려움", "😨", "#537FE7"),
    ("지루함", "🥱", "#7469B6"), ("불안", "😬", "#FFAFCC"),
    ("당황", "😳", "#FFABAB"),   ("외로움", "🥺", "#B6EADA"),
]

# 세션 상태 초기화
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = {name: {} for name in STUDENT_LIST}
if 'hero_pick_history' not in st.session_state:
    st.session_state.hero_pick_history = {}
if 'praise_shower' not in st.session_state:
    st.session_state.praise_shower = {}
if 'student_gift_opening' not in st.session_state:
    st.session_state.student_gift_opening = {}
# [추가] 북소리 애니메이션 완료를 기억하는 세션 상태
if 'student_gift_viewed' not in st.session_state:
    st.session_state.student_gift_viewed = {}

# 오늘, 이번달, 어제
today = date.today()
yesterday = today - timedelta(days=1)
today_key = today.strftime("%Y-%m-%d")
yesterday_key = yesterday.strftime("%Y-%m-%d")

# ---- 페이지 설정 및 사이드바 ----
st.set_page_config(page_title="학급 정서 기록", page_icon="🧡", layout="centered")

# ============ PIN 로그인 추가 ============
if "logged_in_student" not in st.session_state:
    st.session_state.logged_in_student = None

STUDENT_PINS = {
    "김철수": "1111",
    "이영희": "2222", 
    "박민준": "3333",
    "최다은": "4444",
    "정하늘": "5555"
}

if not st.session_state.logged_in_student:
    st.title("🧡 학급 정서 기록")
    st.write("학생 이름과 PIN을 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("이름 선택", STUDENT_LIST)
    with col2:
        pin = st.text_input("PIN (4자리)", type="password", max_chars=4)
    
    if st.button("로그인", use_container_width=True):
        if pin == STUDENT_PINS[name]:
            st.session_state.logged_in_student = name
            st.rerun()
        else:
            st.error("❌ PIN이 틀렸습니다")
    st.stop()

# ============ 로그인 후 메뉴 ============
st.sidebar.write(f"👋 **{st.session
