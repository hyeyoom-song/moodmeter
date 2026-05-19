import streamlit as st

# 무드미터 감정 및 색상(예시)
MOODMETER_EMOTIONS = [
    ("기쁨", "#FFD700"),
    ("감사", "#FFEC8B"),
    ("신남", "#FFA500"),
    ("흥분", "#FF7256"),
    ("평온", "#66CDAA"),
    ("만족", "#90EE90"),
    ("집중", "#48D1CC"),
    ("기대", "#9ACD32"),
    ("슬픔", "#6495ED"),
    ("지루함", "#D3D3D3"),
    ("실망", "#B0C4DE"),
    ("불안", "#CD5C5C"),
    ("분노", "#DC143C"),
    ("짜증", "#FF6347"),
    ("피곤", "#BDB76B"),
    ("불쾌", "#808080"),
]

STUDENTS = [ "홍길동", "김철수", "이영희", "박민수", "최수지" ]  # 학생명 예시

st.set_page_config(
    page_title="학급정서기록",
    page_icon="📝",
    layout="wide"
)

st.title("📝 학급정서기록 - 무드미터 감정기록")

st.정보("학생이 자신의 이름 및 감정을 선택하면 해당 감정에 맞는 색이 자동 표시됩니다. (총 16개 감정)")

with st.form("mood_record_form", clear_on_submit=True):
    name = st.selectbox("학생 이름을 선택하세요.", STUDENTS)
    emotion_names = [e[0] for e in MOODMETER_EMOTIONS]
    emotion = st.selectbox("감정을 선택하세요.", emotion_names)
    color = dict(MOODMETER_EMOTIONS)[emotion]
    st.markdown(f"**선택한 감정 색상:** <span style='color:{color};font-weight:bold;'>{color}</span>", unsafe_allow_html=True)
    submitted = st.form_submit_button("저장")
    if submitted:
        st.success(f"{name} 학생의 감정 '{emotion}' ({color}) 기록이 저장되었습니다. (실제 저장기능은 추후 구현)")

# 아래에 필요하다면 색상표도 보여주기
with st.expander("무드미터 감정별 색상표"):
    cols = st.columns(4)
    for i, (em, col) in enumerate(MOODMETER_EMOTIONS):
        with cols[i % 4]:
            st.markdown(f"<div style='background-color:{col};padding:8px;border-radius:8px;color:white;font-weight:bold;text-align:center'>{em}</div>", unsafe_allow_html=True)
