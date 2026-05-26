import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import calendar

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
st.title("학급정서기록")
st.markdown("초등 담임선생님을 위한 학생 감정 기록 웹앱입니다.")
st.divider()

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

    # 달력에 표시할 연,월 저장 - session_state로 관리
    today = date.today()
    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = today.year
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = today.month

    # 월 이동 화살표 UI 및 연, 월 표시
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
    cal = calendar.Calendar(firstweekday=6)  # 6: Sunday (한국식)  
    month_days = cal.monthdatescalendar(yy, mm)  # 각 주별 날짜 리스트(달력이 5줄 또는 6줄됨)

    # 감정 기록이 있는 부분만 추출
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
                # 타월: 흰색
                z_row.append("#FFFFFF")
                text_row.append("")
                custom_row.append("")
            else:
                mood, color = stu_mood_map.get(d, ("", "#F5F5F5")) # 기록 없으면 연한 회색
                cell = f"{d.day}<br>{mood if mood else ''}"
                z_row.append(color)
                text_row.append(cell)
                custom_row.append(mood)
        z.append(z_row)
        text.append(text_row)
        customdata.append(custom_row)

    # Plotly Figure 생성
    fig = go.Figure(
        data=go.Heatmap(
            z=[[0 for x in range(7)] for y in range(len(z))],  # dummy for heatmap, 실색상은 shape에서 채우기
            x=['일','월','화','수','목','금','토'],
            y=[f"주 {i+1}" for i in range(len(z))],
            showscale=False,
            hoverinfo='text',
            text=text,
            xgap=2, ygap=2,
            colorscale=[[0,"white"], [1,"white"]],  # shape로 채우므로 색상 무의미(white)
        )
    )

    # 날짜 셀 배경색 그리기 및 텍스트 annotation
    for i, week in enumerate(z):
        for j, cell_color in enumerate(week):
            # 배경색 shape 추가
            fig.add_shape(
                type="rect",
                x0=j-0.5, y0=i-0.5,
                x1=j+0.5, y1=i+0.5,
                fillcolor=cell_color,
                line=dict(width=1,color="#e2e2e2"),
                layer="below"
            )
            # 텍스트 annotation
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

    # X,Y 축 세팅
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
        ticktext=["" for _ in range(len(z))],  # y축 레이블 숨김
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

st.set_page_config(page_title="학급정서기록", page_icon="📝")

TAB_LIST = ["오늘의 무드미터", "오늘의 주인공", "오늘의 칭찬샤워"]
tab1, tab2, tab3 = st.tabs(TAB_LIST)

# ===========================  
# 1. 오늘의 무드미터 (기존 코드 그대로)
# ===========================
with tab1:
    # [이하 기존 무드미터 코드 복사/붙여넣기 - 질문의 코드 그대로]
    # ... (생략: 위 질문의 코드를 그대로 이 블록에 넣으세요)
    pass  # 실제코드로 대체

# ===========================
# 2. 오늘의 칭찬샤워
# ===========================
with tab3:
    st.header("오늘의 칭찬샤워 🎉")
    st.markdown("- **학생이름이 적힌 룰렛**에서 Start 버튼을 누르면, 오늘의 칭찬샤워 주인공이 선정됩니다!")

    # 1. session_state에서 오늘 뽑힌 칭찬샤워 학생 기록 조회/저장
    today_str = str(date.today())
    if 'compliment_pick_history' not in st.session_state:
        st.session_state.compliment_pick_history = {}

    # history는 날짜별도 리스트
    if today_str not in st.session_state.compliment_pick_history:
        st.session_state.compliment_pick_history[today_str] = []
        
    today_picked = st.session_state.compliment_pick_history[today_str]

    # Step1: 남은 학생 계산
    remaining = [name for name in STUDENT_LIST if name not in today_picked]
    # 모두 뽑혔으면, 초기화
    if len(remaining) == 0:
        st.session_state.compliment_pick_history[today_str] = []
        remaining = STUDENT_LIST.copy()
        today_picked = []

    # Step2: 룰렛 효과 (아스키 아트 + time.sleep, 혹은 plotly pie/streamlit_drawable_widgets 등 다양한 방식 가능)
    st.write("오늘 칭찬샤워 후보:", ", ".join(f"**{n}**" for n in remaining))
    # 룰렛 그림 구현 - Plotly Pie Chart 사용 (학생이름)
    fig = go.Figure(
        data=[go.Pie(labels=remaining,
                     values=[1]*len(remaining),
                     hole=0.3,
                     marker_colors=['#63cdda', '#ea8685', '#f6b93b', '#78e08f', '#e17055'],
                     textinfo='label')]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

    col_start, _ = st.columns([1,4])
    with col_start:
        if st.button("START!", key=f"roulette-start-{today_str}-{len(today_picked)}"):
            # 룰렛 효과 - 약간의 '돌리는' 느낌 연출 (회전률 랜덤)
            spin_rounds = random.randint(20, 30)
            for i in range(spin_rounds):
                temp_winner = random.choice(remaining)
                fig_spin = go.Figure(
                    data=[go.Pie(labels=remaining,
                                 values=[1]*len(remaining),
                                 hole=0.3,
                                 marker_colors=['#63cdda' if lab!=temp_winner else '#f6b93b' for lab in remaining],
                                 textinfo='label'
                                 )]
                )
                fig_spin.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=350)
                st.plotly_chart(fig_spin, use_container_width=True)
                time.sleep(0.05 + (i/spin_rounds)*0.15)
                st.empty()
            winner = temp_winner
            st.session_state.compliment_pick_history[today_str].append(winner)
            # 효과음 (팡파레) - base64 임베딩 또는 MP3 url(무료)
            st.balloons()
            confetti_mp3_url = "https://cdn.pixabay.com/audio/2022/07/26/audio_124bfa731f.mp3"
            st.audio(confetti_mp3_url, format="audio/mp3", start_time=0)
            st.markdown(
                f"<h1 style='color:#e17055; font-size:48px; text-align:center;'>{winner}</h1>", unsafe_allow_html=True
            )
            st.성공(f"오늘의 주인공은 {winner} 입니다. 🎉 오늘 하루 **{winner}**의 칭찬할 점을 찾아봅시다!")

    # 당첨자 이름 바로 보여주기
    if len(st.session_state.compliment_pick_history[today_str]) > len(today_picked):
        winner = st.session_state.compliment_pick_history[today_str][-1]
        st.markdown(
            f"<h1 style='color:#e17055; font-size:48px; text-align:center;'>{winner}</h1>", unsafe_allow_html=True
        )
        st.성공(f"오늘의 주인공은 {winner} 입니다. 🎉 오늘 하루 **{winner}**의 칭찬할 점을 찾아봅시다!")
