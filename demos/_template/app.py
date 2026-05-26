import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import calendar
import random
import time
import numpy as np

# 감정/색상 정의
MOOD_LIST = [
    ("분노", "#FF5C5C"), ("불안", "#FF8C42"), ("좌절", "#FF8888"), ("초조", "#FFB347"),
    ("신남", "#FFE156"), ("행복", "#FFFF6F"), ("자신감", "#FFD700"), ("의욕", "#FFEF7E"),
    ("슬픔", "#8EC0E4"), ("외로움", "#5465A0"), ("지침", "#95AFBA"), ("실망", "#3B3355"),
    ("평온", "#88D18A"), ("만족", "#B5E6A9"), ("안정", "#3DB36A"), ("감사", "#BEE6CE")
]
MOOD_DICT = dict(MOOD_LIST)
COLOR_DICT = {mood: color for mood, color in MOOD_LIST}
STUDENT_LIST = ["김철수", "이영희", "박민준", "최다은", "정하늘"]

st.set_page_config(page_title="학급정서기록", page_icon="📝")

# ----------- 사이드 메뉴 -----------
st.sidebar.title("MENU")
tab_key = st.sidebar.radio(
    "메뉴를 선택하세요",
    ("오늘의 무드미터", "오늘의 주인공", "오늘의 칭찬샤워"),
    index=0
)

st.title("학급정서기록")
st.markdown("초등 담임선생님을 위한 학생 감정 기록 웹앱입니다.")
st.divider()

# ===========================  
# 1. 오늘의 무드미터
# ===========================
if tab_key == "오늘의 무드미터":
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("날짜 선택", value=date.today())
    with col2:
        selected_student = st.selectbox("학생 선택", STUDENT_LIST)

    st.divider()
    st.markdown("**오늘의 감정을 선택해 주세요**")

    mood_names = [m[0] for m in MOOD_LIST]
    selected_mood = st.radio(
        "감정 선택",
        options=mood_names,
        horizontal=True,
        index=0
    )
    selected_color = MOOD_DICT[selected_mood]

    st.markdown(
        f"<span style='display:inline-block; vertical-align:middle;'>"
        f"<span style='display:inline-block; width:32px; height:32px;"
        f"background:{selected_color}; border-radius:7px; border:1.8px solid #888; margin-right:12px;'></span>"
        f"<span style='font-size:24px; vertical-align:middle; color:#222; font-weight:bold'>{selected_mood}</span></span>",
        unsafe_allow_html=True,
    )

    if 'records' not in st.session_state:
        st.session_state.records = pd.DataFrame(columns=["날짜", "학생", "감정", "색상"])

    if st.button("감정 기록 저장"):
        records = st.session_state.records
        mask = (records["날짜"] == str(selected_date)) & (records["학생"] == selected_student)
        new_row = pd.DataFrame([[str(selected_date), selected_student, selected_mood, selected_color]],
                            columns=["날짜", "학생", "감정", "색상"])
        if mask.any():
            st.session_state.records.loc[mask, ["감정", "색상"]] = (selected_mood, selected_color)
            st.성공(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 수정했습니다.")
        else:
            st.session_state.records = pd.concat([records, new_row], ignore_index=True)
            st.성공(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 저장했습니다.")

    st.divider()
    st.markdown("### 학생별 감정 달력")

    records = st.session_state.records

    if records.empty:
        st.info("아직 감정 기록이 없습니다.")
    else:
        view_student = st.selectbox("달력에서 감정을 보고 싶은 학생을 선택하세요.", STUDENT_LIST, key="calendar_student")

        today = date.today()
        if "calendar_year" not in st.session_state:
            st.session_state.calendar_year = today.year
        if "calendar_month" not in st.session_state:
            st.session_state.calendar_month = today.month

        col_prev, col_month, col_next = st.columns([1,2,1])
        with col_prev:
            if st.button("←", key="prev_month"):
                if st.session_state.calendar_month == 1:
                    st.session_state.calendar_month = 12
                    st.session_state.calendar_year -= 1
                else:
                    st.session_state.calendar_month -= 1
        with col_month:
            st.markdown(
                f"<h5 style='text-align:center'>{st.session_state.calendar_year}년 {st.session_state.calendar_month}월</h5>",
                unsafe_allow_html=True
            )
        with col_next:
            if st.button("→", key="next_month"):
                if st.session_state.calendar_month == 12:
                    st.session_state.calendar_month = 1
                    st.session_state.calendar_year += 1
                else:
                    st.session_state.calendar_month += 1

        yy = st.session_state.calendar_year
        mm = st.session_state.calendar_month
        cal = calendar.Calendar(firstweekday=6)  # 6: Sunday
        month_days = cal.monthdatescalendar(yy, mm)

        stu_df = records[records["학생"] == view_student].copy()
        stu_df['날짜'] = pd.to_datetime(stu_df['날짜'])
        stu_df['date'] = stu_df["날짜"].dt.date
        stu_mood_map = dict(zip(stu_df['date'], zip(stu_df['감정'], stu_df['색상'])))

        z = []
        text = []
        customdata = []
        for week in month_days:
            z_row = []
            text_row = []
            custom_row = []
            for d in week:
                if d.month != mm:
                    z_row.append("#FFFFFF")
                    text_row.append("")
                    custom_row.append("")
                else:
                    mood, color = stu_mood_map.get(d, ("", "#F5F5F5"))
                    cell = f"{d.day}<br>{mood if mood else ''}"
                    z_row.append(color)
                    text_row.append(cell)
                    custom_row.append(mood)
            z.append(z_row)
            text.append(text_row)
            customdata.append(custom_row)

        fig = go.Figure(
            data=go.Heatmap(
                z=[[0 for x in range(7)] for y in range(len(z))],
                x=['일','월','화','수','목','금','토'],
                y=[f"주 {i+1}" for i in range(len(z))],
                showscale=False,
                hoverinfo='text',
                text=text,
                xgap=2, ygap=2,
                colorscale=[[0,"white"], [1,"white"]],
            )
        )

        for i, week in enumerate(z):
            for j, cell_color in enumerate(week):
                fig.add_shape(
                    type="rect",
                    x0=j-0.5, y0=i-0.5,
                    x1=j+0.5, y1=i+0.5,
                    fillcolor=cell_color,
                    line=dict(width=1,color="#e2e2e2"),
                    layer="below"
                )
                ann_text = text[i][j]
                font_color = "#222" if cell_color not in {"#FFFFFF", "#F5F5F5"} else "#AAA"
                fig.add_annotation(
                    x=j, y=i,
                    text=ann_text,
                    showarrow=False,
                    font=dict(color=font_color, size=13),
                    align="center",
                    valign="middle"
                )

        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=['일','월','화','수','목','금','토'],
            side='top',
            showgrid=False,
            zeroline=False
        )
        fig.update_yaxes(
            tickmode='array',
            tickvals=list(range(len(z))),
            ticktext=["" for _ in range(len(z))],
            showgrid=False,
            zeroline=False,
            autorange="reversed"
        )
        fig.update_layout(
            margin=dict(l=10,r=10,t=10,b=10),
            plot_bgcolor="#fafafa",
            paper_bgcolor="#fafafa",
            height=320 if len(z)<6 else 390,
            xaxis_fixedrange=True,
            yaxis_fixedrange=True
        )

        st.plotly_chart(fig, use_container_width=True)

# ===========================  
# 2. 오늘의 주인공 (룰렛)
# ===========================
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
    st.성공(f"오늘의 주인공은 {winner} 입니다. 오늘 하루 **{winner}** 학생과 함께 멋진 하루 보내세요!")

# ===========================
# 3. 오늘의 칭찬샤워 (텍스트위주/룰렛 없음)
# ===========================
elif tab_key == "오늘의 칭찬샤워":
    st.header("오늘의 칭찬샤워 🎉")
    st.markdown("- 오늘 하루 친구들에게 칭찬을 해주고 싶은 '이유'와 '칭찬할 점'을 작성해 보세요!")
    st.info("이 탭에서는 칭찬룰렛 없이 직접 학생이름을 선택해 칭찬 메시지를 저장할 수 있도록 구현하세요.")

    if 'compliment' not in st.session_state:
        st.session_state.compliment = pd.DataFrame(columns=["날짜", "학생", "내용"])

    col1, col2 = st.columns(2)
    with col1:
        compliment_date = st.date_input("날짜 선택 (칭찬 날짜)", value=date.today(), key="compliment_date")
    with col2:
        compliment_student = st.selectbox("칭찬받은 학생 선택", STUDENT_LIST, key="compliment_student")

    compliment_text = st.text_area("칭찬할 점(내용)", key="compliment_text")
    if st.button("칭찬 저장"):
        st.session_state.compliment = pd.concat([
            st.session_state.compliment,
            pd.DataFrame([[str(compliment_date), compliment_student, compliment_text]],
                         columns=["날짜", "학생", "내용"])
        ], ignore_index=True)
        st.성공(f"{compliment_student} 학생의 [{compliment_date}] 칭찬 내용을 등록했습니다!")

    # 칭찬기록(아래)
    st.divider()
    st.markdown("### 칭찬 기록")
    df = st.session_state.compliment
    if df.empty:
        st.info("아직 칭찬 기록이 없습니다.")
    else:
        st.table(df)
