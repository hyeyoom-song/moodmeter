import streamlit as st
import pandas as pd
from datetime import date
import plotly.graph_objects as go
import random
import time

# 학생 목록 및 세션 상태
STUDENT_LIST = ["김철수", "이영희", "박민준", "최다은", "정하늘"]
today_str = str(date.today())
if 'hero_pick_history' not in st.session_state:
    st.session_state.hero_pick_history = {}
if today_str not in st.session_state.hero_pick_history:
    st.session_state.hero_pick_history[today_str] = []

picked = st.session_state.hero_pick_history[today_str]
remaining = [name for name in STUDENT_LIST if name not in picked]
if len(remaining) == 0:
    st.session_state.hero_pick_history[today_str] = []
    remaining = STUDENT_LIST.copy()
    picked = []

st.header("오늘의 주인공 룰렛 🎡")
st.markdown("- Start버튼을 누르면 룰렛이 돌아 오늘의 주인공이 선정됩니다!")
placeholder = st.empty()

def draw_roulette(names, startangle=0, winner_idx=None):
    n = len(names)
    base_colors = ['#63cdda', '#ea8685', '#f6b93b', '#78e08f', '#e17055']
    colors = base_colors * ((n // len(base_colors)) + 1)
    colors = colors[:n]
    if winner_idx is not None:
        colors = [colors[i] if i != winner_idx else "#FFD93D" for i in range(n)]
    fig = go.Figure(go.Pie(
        labels=names, values=[1]*n,
        hole=0, marker_colors=colors, sort=False,
        textinfo='label+percent', rotation=startangle, direction='clockwise'
    ))
    # 화살표(12시 방향)
    fig.add_shape(type="line", x0=0.5, y0=1.05, x1=0.5, y1=1.20,
                  line=dict(color="#ff5555", width=6), xref="paper", yref="paper")
    fig.add_shape(type="path",
            path="M 0.47 1.19 L 0.53 1.19 L 0.5 1.26 Z",
            fillcolor="#ff5555", line=dict(color="#ff5555", width=1), xref="paper", yref="paper")
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, width=410, height=410)
    return fig

# 중앙버튼
c1, c2, c3 = st.columns([2, 2, 1])
with c2:
    start = st.button("START!", key=f"roulette-start-{today_str}-{len(picked)}")

if start 및 len(remaining) > 0:
    n = len(remaining)
    total_angle = 360 * random.randint(3, 5) + random.randint(0, 359)
    steps = 20
    sleep_step = 0.08
    for i in range(steps):
        cur_angle = int(total_angle * (i + 1) / steps)
        placeholder.plotly_chart(draw_roulette(remaining, startangle=cur_angle), use_container_width=True)
        time.sleep(sleep_step + i * 0.005)
    # 마지막: 화살표(12시위치)에 맞는 학생 찾음
    per = 360 / n
    idx = int(((360 - (total_angle % 360) + per/2) % 360) // per)
    winner = remaining[idx]
    st.session_state.hero_pick_history[today_str].append(winner)
    placeholder.plotly_chart(draw_roulette(remaining, startangle=total_angle % 360, winner_idx=idx), use_container_width=True)
    st.balloons()
    st.markdown(
        f"<h1 style='color:#e17055; font-size:48px; text-align:center;'>{winner}</h1>",
        unsafe_allow_html=True
    )
    st.성공(f"오늘의 주인공은 {winner} 입니다!")
else:
    placeholder.plotly_chart(draw_roulette(remaining), use_container_width=True)
    # 당첨자 바로 보여주기(새로고침 시)
    if len(st.session_state.hero_pick_history[today_str]) > len(picked):
        winner = st.session_state.hero_pick_history[today_str][-1]
        st.markdown(
            f"<h1 style='color:#e17055; font-size:48px; text-align:center;'>{winner}</h1>",
            unsafe_allow_html=True
        )
        st.성공(f"오늘의 주인공은 {winner} 입니다!")
