import streamlit as st
import pandas as pd
from datetime import date

# 무드미터 감정/색상 정의 (이전과 동일)
MOOD_LIST = [
    ("분노", "#FF5C5C"), ("불안", "#FF8C42"), ("좌절", "#FF8888"), ("초조", "#FFB347"),
    ("신남", "#FFE156"), ("행복", "#FFFF6F"), ("자신감", "#FFD700"), ("의욕", "#FFEF7E"),
    ("슬픔", "#8EC0E4"), ("외로움", "#5465A0"), ("지침", "#95AFBA"), ("실망", "#3B3355"),
    ("평온", "#88D18A"), ("만족", "#B5E6A9"), ("안정", "#3DB36A"), ("감사", "#BEE6CE"),
]
MOOD_DICT = {name: color for name, color in MOOD_LIST}
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

# 감정 선택 UI - 커스텀 컬러 박스
if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = list(MOOD_DICT.keys())[0]

cols = st.columns(4)
for idx, (mood, color) in enumerate(MOOD_LIST):
    with cols[idx % 4]:
        btn = st.button(
            f"{mood}",
            key=f"mood_{mood}",
            help=mood,
            use_container_width=True
        )
        box_html = f"""
        <div style='
            background:{color};
            color:#222;
            border-radius:10px;
            padding:18px 8px 6px 8px;
            margin-bottom:7px;
            width:100%;
            text-align:center;
            font-weight:bold;
            font-size:17px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);
            border:2px solid #ecebeb;
        '>
            {mood}
        </div>
        """
        st.markdown(box_html, unsafe_allow_html=True)
        if btn:
            st.session_state.selected_mood = mood

# 선택중일 때 테두리 강조
selected_mood = st.session_state.selected_mood
selected_color = MOOD_DICT[selected_mood]
st.markdown(f"#### 선택된 감정: <span style='background:{selected_color}; color:#222; border-radius:9px; padding:4px 15px;'>{selected_mood}</span>", unsafe_allow_html=True)

if "records" not in st.session_state:
    st.session_state.records = pd.DataFrame(
        columns=["날짜", "학생", "감정", "색상"]
    )

if st.button("감정 기록 저장"):
    records = st.session_state.records
    key = (str(selected_date), selected_student)
    mask = (records["날짜"] == str(selected_date)) & (records["학생"] == selected_student)
    new_row = pd.DataFrame(
        [[str(selected_date), selected_student, selected_mood, selected_color]],
        columns=["날짜", "학생", "감정", "색상"]
    )
    if mask.any():
        st.session_state.records.loc[mask, ["감정", "색상"]] = (selected_mood, selected_color)
        st.success(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 수정했습니다.")
    else:
        st.session_state.records = pd.concat([records, new_row], ignore_index=True)
        st.success(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 저장했습니다.")

st.divider()
st.markdown("### 학생별 감정 기록")
records = st.session_state.records
if records.empty:
    st.info("아직 감정 기록이 없습니다.")
else:
    def highlight_mood(s):
        color = s["색상"]
        return [f'background-color: {color}; color: #222; font-weight: bold;' if col=="감정" else '' for col in s.index]
    st.dataframe(
        records.style.apply(highlight_mood, axis=1),
        use_container_width=True,
        height=480
    )
    st.markdown("#### 감정 분포 그래프 (학생별)")
    by_student = records.groupby(["학생", "감정"]).size().unstack(fill_value=0)
    st.bar_chart(by_student)
