import streamlit as st
import pandas as pd
from datetime import date

# 무드미터 기반 감정 및 색상 표
MOOD_LIST = [
    # 빨강 계열 (에너지⬆️, 기분⬇️)
    ("분노", "#FF5C5C"), ("불안", "#FF8C42"), ("좌절", "#FF8888"), ("초조", "#FFB347"),
    # 노랑 계열 (에너지⬆️, 기분⬆️)
    ("신남", "#FFE156"), ("행복", "#FFFF6F"), ("자신감", "#FFD700"), ("의욕", "#FFEF7E"),
    # 파랑 계열 (에너지⬇️, 기분⬇️)
    ("슬픔", "#8EC0E4"), ("외로움", "#5465A0"), ("지침", "#95AFBA"), ("실망", "#3B3355"),
    # 초록 계열 (에너지⬇️, 기분⬆️)
    ("평온", "#88D18A"), ("만족", "#B5E6A9"), ("안정", "#3DB36A"), ("감사", "#BEE6CE"),
]
MOOD_DICT = {name: color for name, color in MOOD_LIST}

# 샘플 학생명 (필요시 명단 수정)
STUDENT_LIST = [
    "김철수", "이영희", "박민준", "최다은", "정하늘"
]

# 페이지 설정
st.set_page_config(
    page_title="학급정서기록",
    page_icon="📝"
)
st.title("학급정서기록")
st.markdown("초등 담임선생님을 위한 학생 감정 기록 웹앱입니다.")

st.divider()

# 날짜 & 학생 선택
col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("날짜 선택", value=date.today())
with col2:
    selected_student = st.selectbox("학생 선택", STUDENT_LIST)

st.divider()

# 감정 선택: 감정명을 컬러 칩으로 표시
def colored_mood_option(mood, color):
    return f'<span style="background-color:{color}; color:#222; border-radius:7px; padding:3px 14px; margin-right:3px;">{mood}</span>'

st.markdown("**오늘의 감정을 선택해 주세요**")
mood_options = [colored_mood_option(mood, color) for mood, color in MOOD_LIST]
mood_names = [mood for mood, color in MOOD_LIST]
mood_choice = st.radio(
    label="무드미터 감정 선택",
    options=mood_names,
    format_func=lambda mood: mood,
    horizontal=True,
)

# 선택 감정 색상 얻기
mood_color = MOOD_DICT[mood_choice]

# 감정 기록 저장: 세션 상태에 데이터프레임으로 임시 저장
if "records" not in st.session_state:
    st.session_state.records = pd.DataFrame(
        columns=["날짜", "학생", "감정", "색상"]
    )

# 저장 버튼
if st.button("감정 기록 저장"):
    # 중복체크: 동일 날짜/학생 기록이 있으면 업데이트, 없으면 추가
    records = st.session_state.records
    key = (str(selected_date), selected_student)
    mask = (records["날짜"] == str(selected_date)) & (records["학생"] == selected_student)
    new_row = pd.DataFrame(
        [[str(selected_date), selected_student, mood_choice, mood_color]],
        columns=["날짜", "학생", "감정", "색상"]
    )
    if mask.any():
        st.session_state.records.loc[mask, ["감정", "색상"]] = (mood_choice, mood_color)
        st.success(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 수정했습니다.")
    else:
        st.session_state.records = pd.concat([records, new_row], ignore_index=True)
        st.success(f"{selected_student} 학생의 [{selected_date}] 감정 기록을 저장했습니다.")

st.divider()

# 전체 기록 테이블 시각화(감정별 배경색)
st.markdown("### 학생별 감정 기록")
records = st.session_state.records
if records.empty:
    st.info("아직 감정 기록이 없습니다.")
else:
    # 색상 적용을 위한 스타일 함수
    def highlight_mood(s):
        color = s["색상"]
        return [f'background-color: {color}; color: #222; font-weight: bold;' if col=="감정" else '' for col in s.index]
    st.dataframe(
        records.style.apply(highlight_mood, axis=1),
        use_container_width=True,
        height=480
    )

    # 학생별, 감정별 분포 간단 시각화 (원형 그래프)
    st
