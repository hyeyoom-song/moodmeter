import streamlit as st
import pandas as pd
from datetime import date

# 감정/색상 정의
MOOD_LIST = [
    ("분노", "#FF5C5C"), ("불안", "#FF8C42"), ("좌절", "#FF8888"), ("초조", "#FFB347"),
    ("신남", "#FFE156"), ("행복", "#FFFF6F"), ("자신감", "#FFD700"), ("의욕", "#FFEF7E"),
    ("슬픔", "#8EC0E4"), ("외로움", "#5465A0"), ("지침", "#95AFBA"), ("실망", "#3B3355"),
    ("평온", "#88D18A"), ("만족", "#B5E6A9"), ("안정", "#3DB36A"), ("감사", "#BEE6CE")
]
MOOD_DICT = dict(MOOD_LIST)
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

def mood_label(mood, color):
    return f"""<span style='display:inline-block; vertical-align:middle;'>\
    <span style='display:inline-block; width:22px; height:22px;\
        background:{color}; border-radius:6px; border:1.5px solid #bebebe; margin-right:7px; vertical-align:middle;'></span>\
    <span style='font-size:18px; vertical-align:middle; color:#222;'>{mood}</span></span>"""

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
st.markdown("### 학생별 감정 기록")
records = st.session_state.records
if records.empty:
    st.info("아직 감정 기록이 없습니다.")
else:
    # 색상 컬럼을 제외한 표시용 데이터프레임 생성
    display_records = records.drop(columns=["색상"])
    def highlight_mood(s):
        # 색상 정보는 records에서 따옴
        color = records.loc[s.name, "색상"]
        return [f'background-color: {color}; color: #222; font-weight: bold;' if col == "감정" else '' for col in s.index]
    st.dataframe(
        display_records.style.apply(highlight_mood, axis=1),
        use_container_width=True,
        height=480
    )
    st.markdown("#### 감정 분포 그래프 (학생별)")
    by_student = records.groupby(["학생", "감정"]).size().unstack(fill_value=0)
    st.bar_chart(by_student)
