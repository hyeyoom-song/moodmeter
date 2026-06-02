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
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = {name: {} for name in STUDENT_LIST}
if 'hero_pick_history' not in st.session_state:
    st.session_state.hero_pick_history = {}
if 'praise_shower' not in st.session_state:
    st.session_state.praise_shower = {}
if 'student_gift_opening' not in st.session_state:
    st.session_state.student_gift_opening = {}
# [추가] 북소리 애니메이션 완료를 기억하는 세션 상태
if 'student_gift_viewed' not in st.session_state:
    st.session_state.student_gift_viewed = {}

# 오늘, 이번달, 어제
today = date.today()
yesterday = today - timedelta(days=1)
today_key = today.strftime("%Y-%m-%d")
yesterday_key = yesterday.strftime("%Y-%m-%d")

# ---- 페이지 설정 및 사이드바 ----
st.set_page_config(page_title="학급 정서 기록", page_icon="🧡", layout="centered")

# ============ PIN 로그인 추가 ============
if "logged_in_student" not in st.session_state:
    st.session_state.logged_in_student = None

STUDENT_PINS = {
    "김철수": "1111",
    "이영희": "2222", 
    "박민준": "3333",
    "최다은": "4444",
    "정하늘": "5555"
}

if not st.session_state.logged_in_student:
    st.title("🧡 학급 정서 기록")
    st.write("학생 이름과 PIN을 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("이름 선택", STUDENT_LIST)
    with col2:
        pin = st.text_input("PIN (4자리)", type="password", max_chars=4)
    
    if st.button("로그인", use_container_width=True):
        if pin == STUDENT_PINS[name]:
            st.session_state.logged_in_student = name
            st.rerun()
        else:
            st.error("❌ PIN이 틀렸습니다")
    st.stop()

# ============ 로그인 후 메뉴 ============
st.sidebar.write(f"👋 **{st.session_state.logged_in_student}** 님")
if st.sidebar.button("로그아웃"):
    st.session_state.logged_in_student = None
    st.rerun()

st.sidebar.title("메뉴")
menu = st.sidebar.radio(
    "이동",
    ["무드미터", "오늘의 주인공", "오늘의 칭찬샤워"],
    index=0,
    key="sidebar_menu"
)


#############################################
# 1. 무드미터 PAGE
#############################################
if menu == "무드미터":
    st.title('학급 정서 기록🧡')
    st.header("오늘의 무드미터")

    # 로그인한 학생 정보 표시
    selected_name = st.session_state.logged_in_student
    st.info(f"😊 {selected_name}의 무드미터를 기록하고 있습니다")

    # 날짜 선택 (년/월/일)
    selected_date = st.date_input(
        "날짜를 선택하세요",
        value=today,
        key="mood_date_picker"
    )
    
    # 선택된 날짜에서 년, 월, 일 추출
    selected_year = selected_date.year
    selected_month = selected_date.month
    selected_day = selected_date.day
    select_ym = f"{selected_year}-{str(selected_month).zfill(2)}"

    # 현재 학생/연월의 데이터
    user_month_data = st.session_state.mood_data[selected_name].setdefault(select_ym, {})
    prev_idx = user_month_data.get(selected_day, None)

    # 감정 선택
    st.subheader("감정을 골라주세요")

    # 선택된 감정 표시 박스
    if prev_idx is not None:
        emo_name, emo_emoji, emo_color = EMOTIONS[prev_idx]
        st.markdown(
            f"<div style='background:{emo_color};padding:10px;border-radius:10px;"
            f"text-align:center;font-size:1.1em;font-weight:bold;margin-bottom:10px;color:#222;'>"
            f"{selected_year}.{str(selected_month).zfill(2)}.{str(selected_day).zfill(2)} 선택, {emo_emoji} {emo_name}</div>",
            unsafe_allow_html=True
        )

    # 4x4 st.button 그리드. 각 버튼은 고유 key를 가짐
    for r in range(4):
        cols = st.columns(4)
        for c in range(4):
            idx = r * 4 + c
            emotion, emoji, color = EMOTIONS[idx]
            is_selected = (prev_idx == idx)
            btn_key = f"emo_btn_{idx}_{selected_name}_{select_ym}_{selected_day}"
            btn_label = f"{emoji} {emotion}"
            if cols[c].button(
                btn_label,
                key=btn_key,
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                user_month_data[selected_day] = idx
                st.session_state.mood_data[selected_name][select_ym] = user_month_data
                st.rerun()

    # 감정 달력 - 월 이동 가능하도록 수정
    st.subheader(f"{selected_name} 감정 달력")
    
    # 달력 표시용 년/월 상태 초기화
    if "calendar_view_year" not in st.session_state:
        st.session_state.calendar_view_year = selected_year
    if "calendar_view_month" not in st.session_state:
        st.session_state.calendar_view_month = selected_month

    # 월 이동 버튼 및 월 표기 - 동일 너비로 조정
    col_prev, col_title, col_next = st.columns([0.5, 2, 0.5])
    with col_prev:
        if st.button("◀", key="calendar_prev", use_container_width=True):
            if st.session_state.calendar_view_month == 1:
                st.session_state.calendar_view_year -= 1
                st.session_state.calendar_view_month = 12
            else:
                st.session_state.calendar_view_month -= 1
            st.rerun()
    with col_next:
        if st.button("▶", key="calendar_next", use_container_width=True):
            if st.session_state.calendar_view_month == 12:
                st.session_state.calendar_view_year += 1
                st.session_state.calendar_view_month = 1
            else:
                st.session_state.calendar_view_month += 1
            st.rerun()
    with col_title:
        st.markdown(
            f"<div style='text-align:center; font-size:2.1em; font-weight:bold;'>"
            f"{st.session_state.calendar_view_year}.{str(st.session_state.calendar_view_month).zfill(2)}</div>",
            unsafe_allow_html=True
        )

    # 달력 표시용 년/월
    cal_year = st.session_state.calendar_view_year
    cal_month = st.session_state.calendar_view_month
    cal_ym = f"{cal_year}-{str(cal_month).zfill(2)}"

    # 달력에 표시할 데이터 가져오기
    cal_month_data = st.session_state.mood_data[selected_name].setdefault(cal_ym, {})

    first_weekday, num_days = calendar.monthrange(cal_year, cal_month)
    # monthrange는 월요일=0 기준이므로, 일요일을 첫 칸으로 두기 위해 보정
    sunday_first_weekday = (first_weekday + 1) % 7

    days_grid = np.full((6, 7), None)
    day = 1
    row, col = 0, sunday_first_weekday
    while day <= num_days:
        days_grid[row][col] = day
        col += 1
        if col > 6:
            row += 1
            col = 0
        day += 1

    week_labels = ['일', '월', '화', '수', '목', '금', '토']
    this_is_today = (today.year == cal_year and today.month == cal_month)
    selected_in_calendar = (selected_year == cal_year and selected_month == cal_month)

    cal_tbl = """
    <style>
    .cal-tdx {min-width:48px;min-height:48px;text-align:center;font-size:0.98em; border-radius:8px; padding:4px;}
    .cal-emoji {font-size:1.13em;}
    .cal-label {font-size:0.78em;}
    </style>
    <table style='border-collapse:collapse;width:100%;'>
    <tr>""" + "".join(
        f"<th style='padding:5px 0 5px 0;border-bottom:1.4px solid #aaa;color:#222;font-weight:bold;font-size:0.98em;'>{w}</th>"
        for w in week_labels
    ) + "</tr>"

    for r in range(6):
        cal_tbl += "<tr>"
        for c in range(7):
            d = days_grid[r][c]
            emoji_cell, label_cell, bgcolor = "", "", "#fafafa"
            is_today = (this_is_today and d == today.day)
            is_selected = (selected_in_calendar and d == selected_day)
            if d is not None:
                em_idx = cal_month_data.get(int(d), None)
                if em_idx is not None:
                    # EMOTIONS에서 직접 색상 가져오기
                    bgcolor = EMOTIONS[em_idx][2]
                    emoji_cell = EMOTIONS[em_idx][1]
                    label_cell = EMOTIONS[em_idx][0]
                
                # 배경색 결정: 오늘이거나 선택된 날짜일 경우 다른 처리
                if is_today or is_selected:
                    final_bgcolor = bgcolor
                    shadow = "box-shadow:inset 0 0 0 3px #FFD93D;"
                else:
                    final_bgcolor = bgcolor
                    shadow = ""
                
                cell_style = (
                    f"background:{final_bgcolor};"
                    "border:1px solid #e4e4e4; border-radius:8px; padding:4px;"
                    + shadow
                )
                cal_tbl += (
                    f"<td class='cal-tdx' style='{cell_style}'>"
                    f"<span class='cal-emoji'>{emoji_cell if emoji_cell else ''}</span><br>"
                    f"<span class='cal-label'>{label_cell if label_cell else ''}</span><br>"
                    f"<span style='font-size:0.98em;font-weight:700;color:#444'>{d}</span></td>"
                )
            else:
                cal_tbl += "<td></td>"
        cal_tbl += "</tr>"
    cal_tbl += "</table>"
    st.markdown(cal_tbl, unsafe_allow_html=True)


#############################################
# 2. 오늘의 주인공 PAGE - 선물 상자 버전
#############################################
elif menu == "오늘의 주인공":
    st.title('학급 정서 기록🧡')
    st.header("오늘의 주인공 🎁")

    current_student = st.session_state.logged_in_student
    
    # 어제 뽑힌 학생은 오늘 룰렛 대상에서 제외
    exclude_name = st.session_state.hero_pick_history.get(yesterday_key, None)
    available_names = [name for name in STUDENT_LIST if name != exclude_name]

    # 오늘 이미 뽑혔으면 고정
    today_hero = st.session_state.hero_pick_history.get(today_key, None)

    # 학생별 세션 상태 초기화
    if current_student not in st.session_state.student_gift_opening:
        st.session_state.student_gift_opening[current_student] = False
    if current_student not in st.session_state.student_gift_viewed:
        st.session_state.student_gift_viewed[current_student] = False

    # 상황 1: 다른 페이지를 갔다 왔고, 이미 오늘 결과를 확인한 학생인 경우 (북소리 패스)
    if st.session_state.student_gift_viewed[current_student] and today_hero:
        st.markdown(
            """
            <div style='text-align:center; margin: 40px 0;'>
                <div style='font-size:180px; margin-bottom:20px;'>🎉</div>
                <div style='font-size:48px; font-weight:bold; color:#e17055; margin-bottom:30px;'>{}</div>
            </div>
            """.format(today_hero),
            unsafe_allow_html=True
        )

    # 상황 2: 아직 '오늘의 주인공 확인' 버튼을 누르기 전인 경우
    elif not st.session_state.student_gift_opening[current_student]:
        st.markdown(
            """
            <div style='text-align:center; margin: 80px 0;'>
                <div style='font-size:120px; display:inline-block;'>🎁</div>
                <div style='font-size:24px; color:#666; margin-top:60px; font-weight:bold;'>오늘의 주인공을 확인하세요!</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            if st.button("🎁 오늘의 주인공 확인", key="open_gift", use_container_width=True):
                st.session_state.student_gift_opening[current_student] = True
                st.rerun()

    # 상황 3: 버튼을 방금 눌러서 처음으로 결과를 확인하는 과정 (북소리 실행)
    else:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(
                """
                <div style='text-align:center; margin: 60px 0;'>
                    <div style='font-size:200px; margin-bottom:20px;'>🥁</div>
                    <div style='font-size:32px; font-weight:bold; color:#e17055; animation: pulse 0.5s infinite;'>
                        두구두구두구두구….
                    </div>
                    <style>
                        @keyframes pulse {
                            0%, 100% { opacity: 1; }
                            50% { opacity: 0.5; }
                        }
                    </style>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # 1초 대기 (북소리 효과)
        time.sleep(1)
        placeholder.empty()
        
        # 주인공 결정 및 표시
        if not today_hero:
            if len(available_names) > 0:
                today_hero = random.choice(available_names)
                st.session_state.hero_pick_history[today_key] = today_hero
            else:
                st.error("선택할 학생이 없습니다!")
                st.session_state.student_gift_opening[current_student] = False
                st.stop()

        # 이제 애니메이션을 완료했으므로 상태 업데이트
        st.session_state.student_gift_viewed[current_student] = True
        
        st.markdown(
            """
            <div style='text-align:center; margin: 40px 0;'>
                <div style='font-size:180px; margin-bottom:20px;'>🎉</div>
                <div style='font-size:48px; font-weight:bold; color:#e17055; margin-bottom:30px;'>{}</div>
            </div>
            """.format(today_hero),
            unsafe_allow_html=True
        )
        st.balloons()


#############################################
# 3. 오늘의 칭찬샤워 PAGE (자동 입력 및 통합 등록 기능)
#############################################
elif menu == "오늘의 칭찬샤워":
    st.title('학급 정서 기록🧡')
    st.header("오늘의 칭찬샤워 💌")
    
    current_student = st.session_state.logged_in_student
    today_hero = st.session_state.hero_pick_history.get(today_key, None)
    
    if not today_hero:
        st.warning("아직 오늘의 주인공이 선정되지 않았습니다! '오늘의 주인공' 탭에서 뽑아주세요.")
    else:
        st.subheader(f"오늘의 주인공: {today_hero}")
        if today_key not in st.session_state.praise_shower:
            st.session_state.praise_shower[today_key] = []

        st.markdown("### 🎤 목소리 또는 타자로 칭찬 남기기")
        st.caption("타자를 쳐도 되고, 타자가 느린 친구들은 [🔴 마이크 켜고 말하기]를 누른 뒤 편하게 이야기하세요!")

        # --- JavaScript + HTML 통합 입력 컴포넌트 ---
        import streamlit.components.v1 as components

        # JavaScript에서 보낸 데이터를 수신하기 위한 쿼리 파라미터 처리
        # 아이들이 [칭찬 남기기]를 눌렀을 때 파이썬이 데이터를 받아서 저장합니다.
        query_params = st.query_params
        if "js_praise_text" in query_params:
            new_praise = query_params["js_praise_text"].strip()
            if new_praise:
                # 튜플 형태로 (작성자, 칭찬내용) 저장
                st.session_state.praise_shower[today_key].append((current_student, new_praise))
                st.success("🎉 칭찬이 정상적으로 등록되었습니다!")
                # 주소창에 남은 파라미터를 청소하고 새로고침
                st.query_params.clear()
                time.sleep(0.5)
                st.rerun()

        # HTML/JS 기반의 마이크 + 입력창 통합 UI 렌더링
        integrated_stt_html = f"""
        <div style="background: #fafafa; padding: 20px; border-radius: 12px; border: 2px dashed #ffb84c; font-family: sans-serif;">
            
            <!-- 1. 음성 인식 제어 버튼 -->
            <div style="text-align: center; margin-bottom: 15px;">
                <button id="start-btn" type="button" style="background-color: #ff7675; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 30px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.2s;">
                    🔴 마이크 켜고 말하기
                </button>
                <p id="status" style="color: #777; margin-top: 8px; font-size: 13px; font-weight: bold;">버튼을 누르고 마이크 권한을 허용해 주세요.</p>
            </div>

            <!-- 2. 실시간 연동 입력창 (말하면 여기에 바로 글자가 써짐) -->
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #444; font-weight: bold;">📝 칭찬 내용 (직접 쓰거나 말해보세요):</label>
                <textarea id="praise-textarea" style="width: 100%; height: 100px; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; resize: vertical; color: #222;" placeholder="{today_hero}에게 하고 싶은 말을 적어보세요..."></textarea>
            </div>

            <!-- 3. 최종 등록 버튼 -->
            <button id="submit-btn" type="button" style="width: 100%; background-color: #4cd137; color: white; border: none; padding: 12px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                💌 이 칭찬 전하기 (등록)
            </button>
        </div>

        <script>
            const startBtn = document.getElementById('start-btn');
            const submitBtn = document.getElementById('submit-btn');
            const statusText = document.getElementById('status');
            const textarea = document.getElementById('praise-textarea');

            // 브라우저 내장 음성인식 엔진 세팅
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            
            if (!SpeechRecognition) {{
                statusText.innerText = "❌ 크롬(Chrome)이나 웨일(Whale) 브라우저를 사용해야 마이크 기능이 작동해요!";
                startBtn.disabled = true;
                startBtn.style.backgroundColor = "#ccc";
            }} else {{
                const recognition = new SpeechRecognition();
                recognition.lang = 'ko-KR';
                recognition.interimResults = true; // 대화 중에 실시간으로 글자가 보이게 설정!!
                recognition.maxAlternatives = 1;

                let finalTranscript = '';

                startBtn.onclick = () => {{
                    try {{
                        recognition.start();
                    }} catch(e) {{
                        // 이미 켜져있는 경우 무시
                    }}
                }};

                recognition.onstart = () => {{
                    statusText.innerText = "🎤 귀를 기울이고 있어요... 말씀해 보세요!";
                    startBtn.style.backgroundColor = "#ffeaa7";
                    startBtn.style.color = "#222";
                    startBtn.innerText = "👂 내 목소리 듣는 중...";
                }};

                recognition.onresult = (event) => {{
                    let interimTranscript = '';
                    for (let i = event.resultIndex; i < event.results.length; ++i) {{
                        if (event.results[i].isFinal) {{
                            finalTranscript += event.results[i][0].transcript + ' ';
                        }} else {{
                            interimTranscript += event.results[i][0].transcript;
                        }}
                    }}
                    // 실시간으로 변환된 텍스트를 입력창에 바로 주입!!!
                    textarea.value = finalTranscript + interimTranscript;
                }};

                recognition.onerror = (event) => {{
                    statusText.innerText = "❌ 마이크 에러! 주소창 옆 마이크 권한을 '허용'해 주세요.";
                    resetMicButton();
                }};

                recognition.onend = () => {{
                    statusText.innerText = "✅ 음성 인식 완료! 마이크가 꺼졌습니다. 수정할 내용이 없다면 아래 등록 버튼을 누르세요.";
                    resetMicButton();
                }};

                function resetMicButton() {{
                    startBtn.style.backgroundColor = "#ff7675";
                    startBtn.style.color = "white";
                    startBtn.innerText = "🔴 마이크 켜고 말하기";
                    finalTranscript = textarea.value; // 인식 끝난 후 글자 유지
                }}
            }}

            // 등록 버튼 클릭 시 Streamlit 서버로 데이터 전송 및 새로고침 유도
            submitBtn.onclick = () => {{
                const val = textarea.value.trim();
                if (!val) {{
                    alert("칭찬 내용을 입력하거나 말해 주세요!");
                    return;
                }}
                // Streamlit의 URL Query Parameter를 이용해 부모 창으로 데이터 전달
                const currentUrl = window.parent.location.href.split('?')[0];
                window.parent.location.href = currentUrl + "?js_praise_text=" + encodeURIComponent(val);
            }};
        </script>
        """
        # 통합 인터페이스 웹 화면에 출력
        components.html(integrated_stt_html, height=310)
        # -----------------------------------------------------

        st.subheader("모두가 남긴 칭찬들 🌻")
        all_praises = st.session_state.praise_shower[today_key]
        if "editing_praise_idx" not in st.session_state:
            st.session_state.editing_praise_idx = None
        if "editing_praise_text" not in st.session_state:
            st.session_state.editing_praise_text = ""

        # 화면 리스트 출력 및 수정 로직
        for idx, item in enumerate(all_praises):
            if isinstance(item, tuple):
                writer, text = item
            else:
                writer, text = "알 수 없음", item

            col1, col2 = st.columns([8, 1])
            with col1:
                if st.session_state.editing_praise_idx == idx:
                    new_text = st.text_area(f"칭찬 수정 ({idx+1})", value=st.session_state.editing_praise_text, key=f"edit_{idx}")
                    save = st.button("저장", key=f"save_{idx}")
                    cancel = st.button("취소", key=f"cancel_{idx}")
                    if save:
                        if new_text.strip():
                            st.session_state.praise_shower[today_key][idx] = (writer, new_text.strip())
                            st.session_state.editing_praise_idx = None
                            st.session_state.editing_praise_text = ""
                            st.success("칭찬이 정상적으로 수정되었습니다!")
                            st.rerun()
                        else:
                            st.warning("수정할 내용을 입력하세요.")
                    if cancel:
                        st.session_state.editing_praise_idx = None
                        st.session_state.editing_praise_text = ""
                        st.rerun()
                else:
                    st.info(f"{idx+1}. {text}")
            with col2:
                if st.session_state.editing_praise_idx != idx:
                    if st.button("수정", key=f"editbtn_{idx}"):
                        st.session_state.editing_praise_idx = idx
                        st.session_state.editing_praise_text = text
                        st.rerun()

        # 엑셀(CSV) 다운로드 데이터프레임 빌드 파트
        if all_praises:
            export_writers = []
            export_texts = []
            for item in all_praises:
                if isinstance(item, tuple):
                    export_writers.append(item[0])
                    export_texts.append(item[1])
                else:
                    export_writers.append("알 수 없음")
                    export_texts.append(item)

            praise_df = pd.DataFrame({
                "주인공": [today_hero] * len(all_praises),
                "날짜": [today_key] * len(all_praises),
                "작성자": export_writers,
                "칭찬": export_texts
            })
            
            csv = praise_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "칭찬샤워 엑셀로 다운로드",
                data=csv,
                file_name=f"praise_{today_key}.csv",
                mime='text/csv'
            )
