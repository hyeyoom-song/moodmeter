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
        st.success(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 수정했습니다.")
    else:
        st.session_state.records = pd.concat([records, new_row], ignore_index=True)
        st.success(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 저장했습니다.")

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

    # 월 이동
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
    month_days = cal.monthdatescalendar(yy, mm)

    # 감정 기록
    stu_df = records[records["학생"] == view_student].copy()
    stu_df['날짜'] = pd.to_datetime(stu_df['날짜'])
    stu_df['date'] = stu_df["날짜"].dt.date
    stu_mood_map = dict(zip(stu_df['date'], stu_df['감정']))

    # 색상 셋업
    mood_to_idx = {mood: i+1 for i, (mood, _) in enumerate(MOOD_LIST)} # 0: 셀없음용
    idx_to_color = ["#FFFFFF"] + [color for (mood, color) in MOOD_LIST]  # 0은 흰색

    z = []
    text = []
    for week in month_days:
        z_row = []
        text_row = []
        for d in week:
            if d.month != mm:
                z_row.append(0)
                text_row.append("")
            else:
                mood = stu_mood_map.get(d, "")
                color_idx = mood_to_idx.get(mood, 0)
                z_row.append(color_idx)
                cell = f"{d.day}<br>{mood}" if mood else f"{d.day}"
                text_row.append(cell)
        z.append(z_row)
        text.append(text_row)

    # colorscale을 감정 색상 그대로 적용 (index 사용)
    n_moods = len(MOOD_LIST)
    colorscale = []
    for i, color in enumerate(idx_to_color):
        colorscale.append([i/(n_moods), color])
        colorscale.append([(i+1)/(n_moods), color])

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=['일','월','화','수','목','금','토'],
            y=[f"주 {i+1}" for i in range(len(z))],
            text=text,
            hoverinfo='text',
            showscale=False,
            colorscale=colorscale,
            xgap=2, ygap=2,
            zmin=0,
            zmax=n_moods
        )
    )

    # 날짜+감정 텍스트 (annotation)
    for i, week in enumerate(z):
        for j, color_idx in enumerate(week):
            ann_text = text[i][j]
            font_color = "#222" if color_idx != 0 else "#AAA"
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
