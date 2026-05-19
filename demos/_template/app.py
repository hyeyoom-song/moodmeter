import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="학급정서기록",
    page_icon="📝",
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

# 🔽 여기가 수정되는 부분입니다!
st.sidebar.markdown("---")
st.sidebar.subheader("CSV 파일 업로드")

uploaded_file = st.sidebar.file_uploader("학생별 무드미터 데이터(CSV)", type=["csv"])

if uploaded_file is not None:
    # 파일이 업로드되면 데이터프레임으로 읽기
    df = pd.read_csv(uploaded_file)
    st.success("CSV 파일이 업로드되었습니다. 전체 데이터를 아래에 보여줍니다.")

    # 데이터프레임 전체 보여주기
    st.dataframe(df)
else:
    # 파일이 업로드되기 전 안내 메시지
    st.info("사이드바에서 CSV를 업로드하세요.")

# 문의 정보
st.sidebar.markdown("---")
st.sidebar.markdown("📌 문의: hyeyoom-song")
