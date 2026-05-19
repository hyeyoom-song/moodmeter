import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go

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
    # 학생 클릭(selectbox)
    view_student = st.selectbox("달력에서 감정을 보고 싶은 학생을 선택하세요.", STUDENT_LIST)

    # 최근 1달(30일) 날짜 목록 생성
    today = date.today()
    first_date = today.replace(day=1)
    days_in_this_month = (today.replace(month=today.month%12+1, day=1) - timedelta(days=1)).day
    month_dates = [first_date + timedelta(days=i) for i in range(days_in_this_month)]

    # 선택 학생의 한 달 감정기록 테이블 생성
    df = records[records["학생"] == view_student].copy()
    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df[df['날짜'].dt.month == today.month]  # 이번 달만

    calendar_df = pd.DataFrame({'날짜': month_dates})
    calendar_df['날짜'] = pd.to_datetime(calendar_df['날짜'])
    merged = pd.merge(calendar_df, df[['날짜', '감정', '색상']], on='날짜', how='left')

    # Plotly로 달력 히트맵 그리기
    merged['day'] = merged['날짜'].dt.day
    merged['weekday'] = merged['날짜'].dt.weekday
    n_weeks = ((calendar_df['날짜'].dt.day.max() + calendar_df['날짜'].dt.weekday.min()) // 7) + 1
    calendar = merged.copy()
    calendar['week'] = ((calendar['day'] + calendar['weekday'].min() - 1) // 7)
    calendar['weekday'] = calendar['날짜'].dt.weekday

    # 달력 셀의 텍스트(감정)
    z_text = calendar['감정'].fillna("").tolist()
    # 달력 셀의 감정색
    z_color = calendar['색상'].fillna("#FFFFFF").tolist()
    days_grid = calendar.pivot(index='week', columns='weekday', values='day')
    mood_grid = calendar.pivot(index='week', columns='weekday', values='감정')
    color_grid = calendar.pivot(index='week', columns='weekday', values='색상').fillna("#FFFFFF")

    # Plotly Heatmap + Annotation
    fig = go.Figure(
        data=go.Heatmap(
            z=[[1]*7 for _ in range(len(days_grid))],  # dummy values
            x=['월', '화', '수', '목', '금', '토', '일'],
            y=[int(i+1) for i in range(len(days_grid))],
            text=days_grid.values,
            hovertemplate="날짜:%{text}<extra></extra>",
            colorscale=[ [0, "white"], [1, "white"] ],  # 색상 직접 입힐 거라 흰색만
            showscale=False
        )
    )

    # 날짜, 감정, 색상별로 색 입히기 & 텍스트 넣기
    for week in days_grid.index:
        for weekday in days_grid.columns:
            day = days_grid.loc[week, weekday]
            if pd.isna(day):  # 빈 칸(해당 달이 아님)
                continue
            mood = str(mood_grid.loc[week, weekday]) if not pd.isna(mood_grid.loc[week, weekday]) else ""
            color = color_grid.loc[week, weekday]
            fig.add_shape(
                type="rect",
                x0=weekday - 0.5, y0=week - 0.5,
                x1=weekday + 0.5, y1=week + 0.5,
                line=dict(width=1, color='#DDD'),
                fillcolor=color
            )
            # 날짜+감정 텍스트
            day_label = str(int(day))
            text = f"<b>{day_label}</b><br>{mood}" if mood else f"<b>{day_label}</b>"
            fig.add_annotation(
                x=weekday, y=week,
                text=text,
                showarrow=False,
                font=dict(color="#111", size=12, family="NanumGothic, Arial")
            )

    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(7)),
        ticktext=['월', '화', '수', '목', '금', '토', '일'],
        showgrid=False,
        zeroline=False
    )
    fig.update_yaxes(
        tickmode='array',
        tickvals=list(days_grid.index),
        ticktext=["" for _ in days_grid.index],  # y축 값 숨김
        showgrid=False,
        zeroline=False,
        autorange="reversed"
    )
    fig.update_layout(
        height=340,
        margin=dict(l=5, r=5, t=30, b=5),
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        title=dict(text=f"{view_student}의 이달 감정기록 캘린더", x=0.5, font=dict(size=16)),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
