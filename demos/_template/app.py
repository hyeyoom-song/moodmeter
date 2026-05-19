import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="학급정서기록",  # 페이지 상단의 제목
    page_icon="📝",  # 브라우저 탭에 표시될 아이콘
    layout="wide"
)

# 제목 및 한 줄 설명
st.title("📝 학급정서기록")
st.markdown("""
초등 담임교사를 위한 감정기록・칭찬샤워・감정변화 그래프 자동화 웹앱입니다.  
CSV 업로드로 학생의 무드미터 변화를 시각적으로 확인할 수 있습니다.
""")

# 사이드바 메뉴
st.sidebar.title("메뉴")
menu = st.sidebar.radio("기능 선택", ("무드미터 감정기록", "칭찬샤워", "감정변화 조회"))

# 메뉴별 기본 골격(틀)
if menu == "무드미터 감정기록":
    st.header("1. 무드미터 감정기록")
    st.정보("학생이 날짜와 이름, 감정 색상, 감정 단어를 선택하고 저장할 수 있습니다.\n저장된 기록은 테이블과 색상표로 시각화됩니다.")
    # [여기에 무드미터 기록 관련 기능 추가 예정]

elif menu == "칭찬샤워":
    st.header("2. 칭찬샤워")
    st.정보("오늘의 주인공 학생을 확인하고, 다른 학생들이 칭찬을 입력할 수 있습니다.\n학부모 알림장용 문구 자동 생성 및 복사 기능도 제공됩니다.")
    # [여기에 칭찬샤워 관련 기능 추가 예정]

elif menu == "감정변화 조회":
    st.header("3. 감정변화 및 칭찬기록 조회")
    st.정보("학생 이름과 조회 기간을 설정하여 감정변화 그래프와 칭찬 내용을 요약할 수 있습니다.\n생기부 작성 초안 문구도 자동 생성됩니다.")
    # [여기에 감정변화 그래프 기능 추가 예정]

# CSV 업로드 예시(향후 3번 메뉴에서 실제 활용)
st.sidebar.subheader("CSV 파일 업로드")
uploaded_file = st.sidebar.file_uploader("학생별 무드미터 데이터(CSV)", type=["csv"])
if uploaded_file:
    st.sidebar.success("CSV 파일이 업로드되었습니다.")

# 사용자를 위한 안내 메시지
st.sidebar.markdown("---")
st.sidebar.markdown("📌 문의: hyeyoom-song")

# (이 이후부터 각 기능을 개발해서 추가)
