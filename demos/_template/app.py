import streamlit as st

# 무드미터의 16개 감정 리스트와 색상 (예시)
moodmeter = [
    {"emotion": "행복", "color": "#f9d423"},
    {"emotion": "기쁨", "color": "#fceabb"},
    {"emotion": "흥분", "color": "#fd746c"},
    {"emotion": "자신감", "color": "#d4fc79"},
    {"emotion": "만족", "color": "#96e6a1"},
    {"emotion": "평온", "color": "#56ccf2"},
    {"emotion": "차분", "color": "#7098d7"},
    {"emotion": "편안", "color": "#b1f8e7"},
    {"emotion": "슬픔", "color": "#173f5f"},
    {"emotion": "실망", "color": "#365073"},
    {"emotion": "외로움", "color": "#557a95"},
    {"emotion": "피곤", "color": "#9baec8"},
    {"emotion": "분노", "color": "#dc143c"},
    {"emotion": "불안", "color": "#f67280"},
    {"emotion": "짜증", "color": "#f8b195"},
    {"emotion": "초조", "color": "#c06c84"},
]

# 사이드바 메뉴
menu = st.sidebar.radio(
    "메뉴를 선택하세요",
    ("첫 페이지", "무드미터 감정기록")
)

if menu == "첫 페이지":
    st.title("무드미터 첫화면")
    st.write("여기는 첫 페이지입니다.")

elif menu == "무드미터 감정기록":
    st.title("오늘 내 감정은?")
    st.write("아래에서 현재 자신의 감정을 선택해보세요.")

    # 감정 버튼 배치 (4x4)
    cols = st.columns(4)
    for idx, mood in enumerate(moodmeter):
        with cols[idx % 4]:
            if st.button(mood["emotion"], key=idx):
                st.success(f"선택한 감정: {mood['emotion']}")
            st.markdown(
                f"<div style='width:32px;height:8px;background-color:{mood['color']};border-radius:4px'></div>",
                unsafe_allow_html=True
            )
