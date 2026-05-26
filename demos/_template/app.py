import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import random
import time
import io

# 학생 목록
STUDENT_LIST = ["김철수", "이영희", "박민준", "최다은", "정하늘"]

# 16가지 감정 정의 (이름, 이모지, 색상)
EMOTIONS = [
    ("행복", "😊", "#FFD93D"),   ("즐거움", "😄", "#FFB84C"),
    ("설렘", "😍", "#FF6D60"),   ("평온", "😌", "#A7FFE4"),
    ("감사", "🙏", "#98D8AA"),   ("자신감", "😎", "#7A9D54"),
    ("힘남", "💪", "#40A2E3"),   ("용기", "🧗‍♂️", "#38E54D"),
    ("슬픔", "😢", "#72A0C1"),   ("피곤", "🥱", "#625772"),
    ("화남", "😡", "#FF8787"),   ("두려움", "😨", "#537FE7"),
    ("지루함", "🥱", "#7469B6"), ("불안", "😬", "#FFAFCC"),
    ("당황", "😳", "#FFABAB"),   ("외로움", "🥺", "#B6EADA"),
]

# 세션 상태 초기화
today_str = str(date.today())
if 'mood_data' not in st.session_state:
    # 형식: {이름: {yyyy-mm: {일: (emotion_idx)}}}
    st.session_state.mood_data = {name: {} for name in STUDENT_LIST}
if 'hero_pick_history' not in st.session_state:
    # {yyyy-mm-dd: 이름}
    st.session_state.hero_pick_history = {}
if 'praise_shower' not in st.session_state:
    # {yyyy-mm-dd: [칭찬글]}
    st.session_state.praise_shower = {}

# 오늘, 이번달, 어제
this_year, this_month = date.today().year, date.today().month
today = date.today()
어제 = today - timedelta(days=1)
today_key = today.strftime("%Y-%m-%d")
어제_key = yesterday.strftime("%Y-%m-%d")

### ---- 사이드바 ----
st.set_page_config(page_title="학급 정서 기록", page_icon="🧡", layout="centered")
st.sidebar.title("메뉴")
menu = st.sidebar.radio(
    "이동",
    ["무드미터", "오늘의 주인공", "오늘의 칭찬샤워"],
    index=0,
    key="sidebar_menu"
)


#############################################
### 1. 무드미터 PAGE
#############################################
if menu == "무드미터":
    st.title('학급 정서 기록🧡')
    st.header("오늘의 무드미터")

    ### (1) 날짜/이름 선택
    col1, col2 = st.columns(2)
    with col1:
        # 월별만 입력받을 수 있도록 제한
        selected_day = st.date_input(
            "날짜를 선택하세요",
            value=today,
            min_value=date(this_year, this_month, 1),
            max_value=date(this_year, this_month, calendar.monthrange(this_year, this_month)[1])
        )
    with col2:
        selected_name = st.selectbox("학생 이름", STUDENT_LIST, key="moodmeter_name")

    select_ym = selected_day.strftime("%Y-%m")
    select_d = selected_day.day

    ### (2) 감정 16개, 4x4, 색상circle+이모지
    st.subheader("감정을 골라주세요")
    emotion_idx = -1
    select_emotion = None
    btn_cols = [st.columns(4) for _ in range(4)]  # 4x4

    # 둥근 버튼 스타일
    btn_css = """
        <style>
        .emotion-btn {
            border-radius: 20px;
            padding: 1rem 0.5rem;
            margin: 0.25rem !important;
            cursor:pointer;
            display:inline-block;
            text-align:center;
            width:100px;
            font-weight:bold;
            font-size:1.5em;
            border:2px solid #eee;
        }
        .emotion-btn.selected {
            border:3px solid #434;
            box-shadow:0 0 10px #FFD93D77;
        }
        </style>
    """
    st.markdown(btn_css, unsafe_allow_html=True)

    # 선택된 감정을 세션에 기록(학생 별)
    if f"emotion_{selected_name}_{select_ym}_{select_d}" not in st.session_state:
        st.session_state[f"emotion_{selected_name}_{select_ym}_{select_d}"] = None

    for r in range(4):
        for c in range(4):
            idx = r * 4 + c
            emotion, emoji, color = EMOTIONS[idx]
            selected = (st.session_state[f"emotion_{selected_name}_{select_ym}_{select_d}"] == idx)
            html = f"""<div class="emotion-btn{' selected' if selected else ''}" style="background:{color};" onclick="var event = new CustomEvent('emotionSelect', {{detail: {idx}}}); document.dispatchEvent(event)">{emoji}<br/><span style="font-size:0.6em;">{emotion}</span></div>"""
            btn_cols[r][c].markdown(html, unsafe_allow_html=True)

    # 자바스크립트로 감정 선택(모서리 둥근 버튼 동작)
    # Streamlit events로 값을 받을 수 없으므로 selectbox로 추가 옵션도 제공
    st.markdown("""
        <script>
        const selEvt = (e) => {window.parent.postMessage({func:'emotionSelected', value:e.detail}, '*');};
        document.removeEventListener('emotionSelect', selEvt);
        document.addEventListener('emotionSelect', selEvt);
        </script>
    """, unsafe_allow_html=True)
    emotion_options = [f"{emoji} {emotion}" for (emotion, emoji, color) in EMOTIONS]
    # 모바일 호환 및 JS 미지원 브라우저 대비
    box_idx = st.selectbox("또는 감정을 선택하세요", options=list(range(len(EMOTIONS))), format_func=lambda x: emotion_options[x])
    # JS에서 값이 오면 세션에 저장
    js_val = st.experimental_get_query_params().get('emotion_idx')
    if js_val:
        # 쿼리파람으로 받은 경우 강제 적용
        st.session_state[f"emotion_{selected_name}_{select_ym}_{select_d}"] = int(js_val[0])
    elif box_idx is not None:
        st.session_state[f"emotion_{selected_name}_{select_ym}_{select_d}"] = int(box_idx)

    emotion_idx = st.session_state[f"emotion_{selected_name}_{select_ym}_{select_d}"]

    # (3) 감정 입력 버튼
    if st.button("감정 입력"):
        if emotion_idx is not None:
            # 학생별, 월별 기록 저장
            user_month_data = st.session_state.mood_data[selected_name].setdefault(select_ym, {})
            user_month_data[select_d] = emotion_idx
            st.success(f"{selected_name} 학생의 감정이 저장되었습니다!")
        else:
            st.warning("감정을 선택해주세요.")

#############################################
### 2. 오늘의 주인공 PAGE
#############################################
elif menu == "오늘의 주인공":
    st.title('학급 정서 기록🧡')
    st.header("오늘의 주인공 룰렛 🎡")

    # 룰렛 대상 학생 리스트 생성
    # 어제 뽑힌 학생은 오늘 룰렛 대상에서 빼지만 종합 리스트에는 보임
    exclude_name = st.session_state.hero_pick_history.get(어제_key, None)
    roulette_names = STUDENT_LIST.copy()
    available_names = [name for name in STUDENT_LIST if name != exclude_name]
    
    # 오늘 이미 뽑혔으면 고정
    today_hero = st.session_state.hero_pick_history.get(today_key, None)

    # 룰렛 그리기 함수
    def draw_roulette(names, startangle=0, winner_idx=None):
        n = len(names)
        base_colors = ['#63cdda', '#ea8685', '#f6b93b', '#78e08f', '#e17055']
        colors = (base_colors * ((n//len(base_colors))+1))[:n]
        if winner_idx is not None:
            colors = [colors[i] if i != winner_idx else "#FFD93D" for i in range(n)]
        fig = go.Figure(go.Pie(
            labels=names, values=[1]*n,
            hole=0, marker_colors=colors, sort=False,
            textinfo='label+percent', rotation=startangle, direction='clockwise'
        ))
        fig.add_shape(type="line", x0=0.5, y0=1.05, x1=0.5, y1=1.20,
                      line=dict(color="#ff5555", width=6), xref="paper", yref="paper")
        fig.add_shape(type="path",
                path="M 0.47 1.19 L 0.53 1.19 L 0.5 1.26 Z",
                fillcolor="#ff5555", line=dict(color="#ff5555", width=1), xref="paper", yref="paper")
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, width=410, height=410)
        return fig

    placeholder = st.empty()
    c1, c2, c3 = st.columns([2,2,1])
    with c2:
        start = st.button("START!", key=f"roulette-start-{today_key}")

    winner = None

    if today_hero:  # 이미 오늘 선정된 주인공이 있는 경우 고정
        winner = today_hero
        idx = roulette_names.index(winner)
        placeholder.plotly_chart(draw_roulette(roulette_names, winner_idx=idx), use_container_width=True)
        st.balloons()
        st.success(f"오늘의 주인공은 {winner}입니다. {winner}과 함께 멋진 하루 보내세요!")
    elif start and len(available_names) > 0:
        # 룰렛 동작 (오늘 선정된 주인공이 없다면 뽑기 로직 작동)
        n = len(available_names)
        total_angle = 360 * random.randint(3, 5) + random.randint(0, 359)
        steps = 20
        sleep_step = 0.08
        for i in range(steps):
            cur_angle = int(total_angle * (i + 1) / steps)
            placeholder.plotly_chart(draw_roulette(available_names, startangle=cur_angle), use_container_width=True)
            time.sleep(sleep_step + i * 0.005)
        per = 360 / n
        idx = int(((360 - (total_angle % 360) + per / 2) % 360) // per)
        winner = available_names[idx]
        st.session_state.hero_pick_history[today_key] = winner
        # 룰렛판에는 전체 학생, 색만 강조
        placeholder.plotly_chart(draw_roulette(roulette_names, winner_idx=roulette_names.index(winner)), use_container_width=True)
        st.balloons()
        # 👇 주인공 이름 크게 중앙에 띄우기
        st.markdown(
            f"<h1 style='color:#e17055; font-size:48px; text-align:center;'>{winner}</h1>",
            unsafe_allow_html=True
        )
        st.success(f"오늘의 주인공은 {winner}입니다. {winner}과 함께 멋진 하루 보내세요!")
    
    else:
        # 최초 페이지 진입/아직 주인공 없음, 룰렛 그림 출력
        placeholder.plotly_chart(draw_roulette(roulette_names), use_container_width=True)
        # 만약 주인공이 오늘 뽑혔다면 이름 강조
        if today_hero:
            st.success(f"오늘의 주인공은 {today_hero}입니다. {today_hero}과 함께 멋진 하루 보내세요!")
        else:
            st.info("아직 주인공이 선정되지 않았습니다!")


#############################################
### 3. 오늘의 칭찬샤워 PAGE
#############################################
elif menu == "오늘의 칭찬샤워":
    st.title('학급 정서 기록🧡')
    st.header("오늘의 칭찬샤워 💌")
    today_hero = st.session_state.hero_pick_history.get(today_key, None)
    if not today_hero:
        st.warning("아직 오늘의 주인공이 선정되지 않았습니다! '오늘의 주인공' 탭에서 뽑아주세요.")
    else:
        st.subheader(f"오늘의 주인공: {today_hero}")
        if today_key not in st.session_state.praise_shower:
            st.session_state.praise_shower[today_key] = []

        # 칭찬 남기기
        praise_text = st.text_area(f"{today_hero}에게 칭찬 한마디 남기기!", key="praise_text")
        if st.button("칭찬 남기기"):
            if praise_text.strip():
                st.session_state.praise_shower[today_key].append(praise_text.strip())
                st.success("칭찬이 정상적으로 등록되었습니다!")
            else:
                st.warning("칭찬을 입력해 주세요.")

        # 수정 기능 구현
        st.subheader("모두가 남긴 칭찬들 🌻")
        all_praises = st.session_state.praise_shower[today_key]
        if "editing_praise_idx" not in st.session_state:
            st.session_state.editing_praise_idx = None
        if "editing_praise_text" not in st.session_state:
            st.session_state.editing_praise_text = ""

        for idx, text in enumerate(all_praises):
            col1, col2 = st.columns([8, 1])
            with col1:
                # 수정중인 칭찬이면 텍스트에디트 활성화
                if st.session_state.editing_praise_idx == idx:
                    new_text = st.text_area(f"칭찬 수정 ({idx+1})", value=st.session_state.editing_praise_text, key=f"edit_{idx}")
                    save = st.button("저장", key=f"save_{idx}")
                    cancel = st.button("취소", key=f"cancel_{idx}")
                    if save:
                        if new_text.strip():
                            st.session_state.praise_shower[today_key][idx] = new_text.strip()
                            st.session_state.editing_praise_idx = None
                            st.session_state.editing_praise_text = ""
                            st.success("칭찬이 정상적으로 수정되었습니다!")
                            st.experimental_rerun()
                        else:
                            st.warning("수정할 내용을 입력하세요.")
                    if cancel:
                        st.session_state.editing_praise_idx = None
                        st.session_state.editing_praise_text = ""
                        st.experimental_rerun()
                else:
                    st.정보(f"{idx+1}. {text}")
            with col2:
                if st.session_state.editing_praise_idx != idx:
                    if st.button("수정", key=f"editbtn_{idx}"):
                        st.session_state.editing_praise_idx = idx
                        st.session_state.editing_praise_text = text
                        st.experimental_rerun()

        # 엑셀 다운로드 기능
        if all_praises:
            import pandas as pd
            praise_df = pd.DataFrame({
                "주인공": [today_hero]*len(all_praises),
                "날짜": [today_key]*len(all_praises),
                "칭찬": all_praises
            })
            csv = praise_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("칭찬샤워 엑셀로 다운로드", data=csv, file_name=f"praise_{today_key}.csv", mime='text/csv')
