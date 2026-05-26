import streamlit as st
import pandas as pd
from datetime import date
import plotly.graph_objects as go
import random
import time

st.set_page_config(page_title="무드미터 & 주인공 & 칭찬샤워", page_icon="😊", layout="centered")
st.title("😊 무드미터 & 오늘의 주인공 & 칭찬샤워")

# 학생 목록
STUDENT_LIST = ["김철수", "이영희", "박민준", "최다은", "정하늘"]
today_str = str(date.today())

# 탭 생성
tabs = st.tabs(["무드미터", "오늘의 주인공", "오늘의 칭찬샤워"])

# 1. 무드미터 탭
with tabs[0]:
    st.header("오늘의 무드미터 😄")
    # 무드미터 데이터 보관
    mood_options = {
        "행복😁": "yellow",
        "슬픔😢": "blue",
        "화남😠": "red",
        "긴장😬": "purple",
        "놀람😮": "green",
        "지루함😐": "gray"
    }
    if 'mood_data' not in st.session_state:
        st.session_state.mood_data = {name: [] for name in STUDENT_LIST}
    
    select_name = st.selectbox("이름을 선택하세요", STUDENT_LIST, key="mood_name")
    select_mood = st.radio("오늘의 기분은?", list(mood_options.keys()), horizontal=True, key="mood_radio")
    submit = st.button("무드 기록", key="mood_submit")
    if submit:
        st.session_state.mood_data[select_name].append({"date": today_str, "mood": select_mood})
        st.success(f"{select_name}님의 기분이 '{select_mood}'로 기록되었습니다!")

    # 집계 데이터프레임 만들기
    mood_df = []
    for name in STUDENT_LIST:
        for m in st.session_state.mood_data[name]:
            if m["date"] == today_str:
                mood_df.append({"name": name, "mood": m["mood"]})
    if mood_df:
        mood_df = pd.DataFrame(mood_df)
        mood_count = mood_df.groupby("mood").count()["name"]
        st.subheader("오늘 입력된 전체 무드")
        st.bar_chart(mood_count)
    else:
        st.info("아직 입력된 감정이 없습니다.")

# 2. 오늘의 주인공 탭
with tabs[1]:
    st.header("오늘의 주인공 룰렛 🎡")
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

    # 룰렛 그리기 함수
    def draw_roulette(names, startangle=0, winner_idx=None):
        n = len(names)
        base_colors = ['#63cdda', '#ea8685', '#f6b93b', '#78e08f', '#e17055']
        colors = (base_colors * ((n//len(base_colors)) + 1))[:n]
        if winner_idx is not None:
            colors = [colors[i] if i != winner_idx else "#FFD93D" for i in range(n)]
        fig = go.Figure(go.Pie(
            labels=names, values=[1]*n,
            hole=0, marker_colors=colors, sort=False,
            textinfo='label+percent', rotation=startangle, direction='clockwise'
        ))
        fig.add_shape(type="line", x0=0.5, y0=1.05, x1=0.5, y1=1.20,
                      line=dict(color="#ff5555", width=6), xref="paper", yref="paper")
        fig.add_shape(type="path",
                path="M 0.47 1.19 L 0.53 1.19 L 0.5 1.26 Z",
                fillcolor="#ff5555", line=dict(color="#ff5555", width=1), xref="paper", yref="paper")
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, width=410, height=410)
        return fig

    placeholder = st.empty()
    c1, c2, c3 = st.columns([2, 2, 1])
    with c2:
        start = st.button("START!", key=f"roulette-start-{today_str}-{len(picked)}")

    if start and len(remaining) > 0:
        n = len(remaining)
        total_angle = 360 * random.randint(3, 5) + random.randint(0, 359)
        steps = 20
        sleep_step = 0.08
        for i in range(steps):
            cur_angle = int(total_angle * (i + 1) / steps)
            placeholder.plotly_chart(draw_roulette(remaining, startangle=cur_angle), use_container_width=True)
            time.sleep(sleep_step + i * 0.005)
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
        st.success(f"오늘의 주인공은 {winner} 입니다!")
    else:
        placeholder.plotly_chart(draw_roulette(remaining), use_container_width=True)
        if len(st.session_state.hero_pick_history[today_str]) > 0:
            winner = st.session_state.hero_pick_history[today_str][-1]
            st.markdown(
                f"<h1 style='color:#e17055; font-size:48px; text-align:center;'>{winner}</h1>",
                unsafe_allow_html=True
            )
            st.success(f"오늘의 주인공은 {winner} 입니다!")

# 3. 오늘의 칭찬샤워 탭
with tabs[2]:
    st.header("오늘의 칭찬샤워 💌")
    # 오늘의 주인공 결정 여부 확인
    if ('hero_pick_history' in st.session_state and 
        today_str in st.session_state.hero_pick_history and
        len(st.session_state.hero_pick_history[today_str]) > 0):
        today_hero = st.session_state.hero_pick_history[today_str][-1]
        st.subheader(f"오늘의 주인공: {today_hero}")
        if 'praise_shower' not in st.session_state:
            st.session_state.praise_shower = {}
        if today_str not in st.session_state.praise_shower:
            st.session_state.praise_shower[today_str] = []

        praise_text = st.text_area(f"{today_hero}에게 칭찬 한마디 남기기!", key="praise_text")
        send = st.button("칭찬 남기기", key="praise_send")
        if send and praise_text.strip():
            st.session_state.praise_shower[today_str].append(praise_text.strip())
            st.success("칭찬이 정상적으로 등록되었습니다!")
        elif send and not praise_text.strip():
            st.warning("칭찬을 입력해 주세요.")

        # 오늘의 칭찬샤워 목록
        st.subheader("모두가 남긴 칭찬들 🌻")
        for idx, t in enumerate(st.session_state.praise_shower[today_str], 1):
            st.info(f"{idx}. {t}")

    else:
        st.warning("아직 오늘의 주인공이 선정되지 않았습니다. '오늘의 주인공' 탭에서 뽑아주세요.")
