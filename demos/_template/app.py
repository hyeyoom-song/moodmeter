import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import random
import time
import io

# 학생 목록
STUDENT_LIST = ["김철수", "이영희", "박민준", "최다은", "정하늘"]

# 16가지 감정 정의 (이름, 이모지, 색상, 감정점수[-5~+5])
# 점수 기준: 쾌적도(+) × 에너지(×) 조합으로 직관적으로 산정
# 예) 행복(고에너지+고쾌) = +5, 평온(저에너지+쾌) = +3, 슬픔(저에너지+불쾌) = -3, 화남(고에너지+불쾌) = -5
EMOTIONS = [
    ("행복",   "😊", "#FFD93D", 5),
    ("즐거움", "😄", "#FFB84C", 4),
    ("설렘",   "😍", "#FF6D60", 4),
    ("평온",   "😌", "#A7FFE4", 3),
    ("감사",   "🙏", "#98D8AA", 3),
    ("자신감", "😎", "#7A9D54", 4),
    ("힘남",   "💪", "#40A2E3", 3),
    ("용기",   "🧗", "#38E54D", 3),
    ("슬픔",   "😢", "#72A0C1",-3),
    ("피곤",   "🥱", "#625772",-2),
    ("화남",   "😡", "#FF8787",-5),
    ("두려움", "😨", "#537FE7",-4),
    ("지루함", "😑", "#7469B6",-2),
    ("불안",   "😬", "#FFAFCC",-3),
    ("당황",   "😳", "#FFABAB",-2),
    ("외로움", "🥺", "#B6EADA",-3),
]

EMOTION_SCORE = {e[0]: e[3] for e in EMOTIONS}
TIMES = ["오전", "오후"]

# ── 세션 상태 초기화 ──────────────────────────────────────────────────────────
def init_session():
    defaults = {
        # mood_data[이름][YYYY-MM][day]["오전"/"오후"] = emotion_idx
        "mood_data": {name: {} for name in STUDENT_LIST + ["선생님"]},
        # hero_schedule[YYYY-MM] = [이름순서...] (셔플된 배정표)
        "hero_schedule": {},
        # hero_pick_history[YYYY-MM-DD] = 이름 (실제 뽑힌 날 기록, 역방향 조회용)
        "hero_pick_history": {},
        "praise_shower": {},
        "student_gift_opening": {},
        "student_gift_viewed": {},
        "hero_revealed": {},
        "logged_in_student": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # 기존 코드와의 호환: 선생님 키 보장
    if "선생님" not in st.session_state.mood_data:
        st.session_state.mood_data["선생님"] = {}

init_session()

# 오늘, 어제
today = date.today()
yesterday = today - timedelta(days=1)
today_key = today.strftime("%Y-%m-%d")
yesterday_key = yesterday.strftime("%Y-%m-%d")
this_ym = today.strftime("%Y-%m")

# ── 오늘의 주인공 월별 배정 로직 ─────────────────────────────────────────────
def get_hero_schedule(ym: str) -> list:
    """해당 월의 주인공 배정표를 반환. 없으면 랜덤 셔플해서 생성."""
    if ym not in st.session_state.hero_schedule:
        shuffled = STUDENT_LIST.copy()
        random.shuffle(shuffled)
        st.session_state.hero_schedule[ym] = shuffled
    return st.session_state.hero_schedule[ym]

def get_today_hero(target_date: date) -> str:
    """target_date의 주인공을 반환. 해당 월 배정표에서 날짜 순서대로 배정."""
    ym = target_date.strftime("%Y-%m")
    schedule = get_hero_schedule(ym)
    # 해당 월의 몇 번째 수업일인지 (단순히 day-1 을 학생수로 나눈 나머지)
    # 배정: 1일→schedule[0], 2일→schedule[1], ..., 학생수 초과 시 순환
    idx = (target_date.day - 1) % len(schedule)
    hero = schedule[idx]
    # 기록
    date_key = target_date.strftime("%Y-%m-%d")
    if date_key not in st.session_state.hero_pick_history:
        st.session_state.hero_pick_history[date_key] = hero
    return hero

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="학급 정서 기록", page_icon="🧡", layout="centered")

# ── PIN 로그인 ─────────────────────────────────────────────────────────────────
STUDENT_PINS = {
    "선생님": "0000",
    "김철수": "1111",
    "이영희": "2222",
    "박민준": "3333",
    "최다은": "4444",
    "정하늘": "5555",
}

if not st.session_state.logged_in_student:
    st.title("🧡 학급 정서 기록")
    st.write("학생 이름과 PIN을 입력하세요")
    col1, col2 = st.columns(2)
    with col1:
        name = st.selectbox("이름 선택", ["선생님"] + STUDENT_LIST)
    with col2:
        pin = st.text_input("PIN (4자리)", type="password", max_chars=4)
    if st.button("로그인", use_container_width=True):
        if pin == STUDENT_PINS[name]:
            st.session_state.logged_in_student = name
            st.rerun()
        else:
            st.error("❌ PIN이 틀렸습니다")
    st.stop()

# ── 사이드바 ──────────────────────────────────────────────────────────────────
st.sidebar.write(f"👋 **{st.session_state.logged_in_student}** 님")
if st.sidebar.button("로그아웃"):
    st.session_state.logged_in_student = None
    st.rerun()

st.sidebar.title("메뉴")
is_teacher = (st.session_state.logged_in_student == "선생님")

if is_teacher:
    menu_options = [
        "🎨 무드미터",
        "📈 감정 그래프",
        "👥 오늘의 학급 감정",
        "🎁 오늘의 주인공",
        "📅 이달의 배정표",
        "💌 오늘의 칭찬샤워",
    ]
else:
    menu_options = [
        "🎨 무드미터",
        "📈 감정 그래프",
        "🎁 오늘의 주인공",
        "💌 오늘의 칭찬샤워",
    ]

menu = st.sidebar.radio(
    "이동",
    menu_options,
    index=0,
    key="sidebar_menu",
)

#############################################
# 1. 🎨 무드미터 PAGE (오전/오후 분리)
#############################################
if menu == "🎨 무드미터":
    st.title("학급 정서 기록🧡")
    st.header("오늘의 무드미터")

    selected_name = st.session_state.logged_in_student
    st.info(f"😊 {selected_name}의 무드미터를 기록하고 있습니다")

    selected_date = st.date_input("날짜를 선택하세요", value=today, key="mood_date_picker")
    selected_year  = selected_date.year
    selected_month = selected_date.month
    selected_day   = selected_date.day
    select_ym = f"{selected_year}-{str(selected_month).zfill(2)}"

    # mood_data 구조: [이름][YYYY-MM][day][시간대] = idx
    user_month_data = st.session_state.mood_data[selected_name].setdefault(select_ym, {})
    day_data = user_month_data.setdefault(selected_day, {})   # {"오전": idx, "오후": idx}

    # ── 오전 / 오후 탭 ────────────────────────────────────────────────────────
    tab_am, tab_pm = st.tabs(["🌤 오전", "🌆 오후"])

    for tab, time_slot in [(tab_am, "오전"), (tab_pm, "오후")]:
        with tab:
            prev_idx = day_data.get(time_slot, None)

            if prev_idx is not None:
                emo_name, emo_emoji, emo_color, _ = EMOTIONS[prev_idx]
                st.markdown(
                    f"<div style='background:{emo_color};padding:10px;border-radius:10px;"
                    f"text-align:center;font-size:1.1em;font-weight:bold;margin-bottom:10px;color:#222;'>"
                    f"{selected_year}.{str(selected_month).zfill(2)}.{str(selected_day).zfill(2)} "
                    f"[{time_slot}] {emo_emoji} {emo_name}</div>",
                    unsafe_allow_html=True,
                )

            st.subheader(f"{time_slot} 감정을 골라주세요")
            for r in range(4):
                cols = st.columns(4)
                for c in range(4):
                    idx = r * 4 + c
                    emotion, emoji, color, score = EMOTIONS[idx]
                    is_selected = (prev_idx == idx)
                    btn_key = f"emo_{time_slot}_{idx}_{selected_name}_{select_ym}_{selected_day}"
                    if cols[c].button(
                        f"{emoji} {emotion}",
                        key=btn_key,
                        use_container_width=True,
                        type="primary" if is_selected else "secondary",
                    ):
                        day_data[time_slot] = idx
                        user_month_data[selected_day] = day_data
                        st.session_state.mood_data[selected_name][select_ym] = user_month_data
                        st.rerun()

    # ── 달력 ──────────────────────────────────────────────────────────────────
    st.subheader(f"{selected_name} 감정 달력")
    st.caption("오전·오후 두 칸으로 표시됩니다")

    if "calendar_view_year"  not in st.session_state: st.session_state.calendar_view_year  = selected_year
    if "calendar_view_month" not in st.session_state: st.session_state.calendar_view_month = selected_month

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
            f"<div style='text-align:center;font-size:2.1em;font-weight:bold;'>"
            f"{st.session_state.calendar_view_year}.{str(st.session_state.calendar_view_month).zfill(2)}</div>",
            unsafe_allow_html=True,
        )

    cal_year  = st.session_state.calendar_view_year
    cal_month = st.session_state.calendar_view_month
    cal_ym    = f"{cal_year}-{str(cal_month).zfill(2)}"
    cal_month_data = st.session_state.mood_data[selected_name].setdefault(cal_ym, {})

    first_weekday, num_days = calendar.monthrange(cal_year, cal_month)
    sunday_first_weekday = (first_weekday + 1) % 7

    days_grid = np.full((6, 7), None)
    day, row, col = 1, 0, sunday_first_weekday
    while day <= num_days:
        days_grid[row][col] = day
        col += 1
        if col > 6: row, col = row + 1, 0
        day += 1

    week_labels = ["일", "월", "화", "수", "목", "금", "토"]
    this_is_today = (today.year == cal_year and today.month == cal_month)
    selected_in_calendar = (selected_year == cal_year and selected_month == cal_month)

    # 달력 HTML – 각 셀에 오전(위)/오후(아래) 두 행 표시
    cal_tbl = """
    <style>
    .cal-tdx{min-width:44px;text-align:center;font-size:0.9em;border-radius:8px;padding:3px;}
    .cal-slot{border-radius:5px;padding:1px 2px;font-size:0.78em;margin:1px 0;line-height:1.3;}
    </style>
    <table style='border-collapse:collapse;width:100%;'>
    <tr>""" + "".join(
        f"<th style='padding:5px 0;border-bottom:1.4px solid #aaa;color:#222;font-weight:bold;font-size:0.98em;'>{w}</th>"
        for w in week_labels
    ) + "</tr>"

    for r in range(6):
        cal_tbl += "<tr>"
        for c in range(7):
            d = days_grid[r][c]
            if d is None:
                cal_tbl += "<td></td>"
                continue

            day_dict = cal_month_data.get(int(d), {})
            is_today    = this_is_today and (d == today.day)
            is_selected = selected_in_calendar and (d == selected_day)
            shadow = "box-shadow:inset 0 0 0 3px #FFD93D;" if (is_today or is_selected) else ""

            slots_html = ""
            for ts in ["오전", "오후"]:
                em_idx = day_dict.get(ts, None) if isinstance(day_dict, dict) else None
                if em_idx is not None:
                    e_name, e_emoji, e_color, _ = EMOTIONS[em_idx]
                    slots_html += (
                        f"<div class='cal-slot' style='background:{e_color};color:#222;'>"
                        f"{e_emoji}<br><span style='font-size:0.7em'>{ts}</span></div>"
                    )
                else:
                    slots_html += f"<div class='cal-slot' style='color:#bbb;font-size:0.7em;'>{ts} -</div>"

            cal_tbl += (
                f"<td class='cal-tdx' style='border:1px solid #e4e4e4;border-radius:8px;padding:3px;{shadow}'>"
                f"<span style='font-size:0.9em;font-weight:700;color:#444'>{d}</span>"
                f"{slots_html}</td>"
            )
        cal_tbl += "</tr>"
    cal_tbl += "</table>"
    st.markdown(cal_tbl, unsafe_allow_html=True)

#############################################
# 2. 📈 감정 그래프 PAGE
#############################################
elif menu == "📈 감정 그래프":
    st.title("학급 정서 기록🧡")
    st.header("📈 감정 흐름 그래프")

    selected_name = st.session_state.logged_in_student

    # 대상자 선택 (선생님은 본인 포함 전체 선택 가능)
    if selected_name == "선생님":
        view_name = st.selectbox("대상 선택", ["선생님"] + STUDENT_LIST, key="graph_student_sel")
    else:
        view_name = selected_name
        st.info(f"😊 {view_name}의 감정 흐름")

    # 기간 선택
    view_ym = st.selectbox(
        "월 선택",
        options=[f"{today.year}-{str(m).zfill(2)}" for m in range(1, 13)],
        index=today.month - 1,
        key="graph_ym_sel",
    )

    month_data = st.session_state.mood_data.get(view_name, {}).get(view_ym, {})

    # 날짜-시간대별 점수 수집
    records = []
    year, month = map(int, view_ym.split("-"))
    _, num_days = calendar.monthrange(year, month)
    for day in range(1, num_days + 1):
        day_dict = month_data.get(day, {})
        if not isinstance(day_dict, dict):
            continue
        for ts in ["오전", "오후"]:
            em_idx = day_dict.get(ts)
            if em_idx is not None:
                name, emoji, color, score = EMOTIONS[em_idx]
                records.append({
                    "날짜": f"{view_ym}-{str(day).zfill(2)} {ts}",
                    "감정": f"{emoji} {name}",
                    "점수": score,
                    "색상": color,
                    "emoji": emoji,
                })

    if not records:
        st.info("아직 기록된 감정 데이터가 없습니다. 무드미터에서 먼저 기록해주세요!")
    else:
        df = pd.DataFrame(records)

        # ── 감정선 그래프 ──────────────────────────────────────────────────────
        fig = go.Figure()

        # 배경 색 띠: 긍정(녹색), 중립(회색), 부정(빨강)
        fig.add_hrect(y0=0, y1=5,   fillcolor="rgba(152,216,170,0.15)", line_width=0)
        fig.add_hrect(y0=-5, y1=0,  fillcolor="rgba(255,135,135,0.15)", line_width=0)
        fig.add_hline(y=0, line_dash="dot", line_color="#aaa", line_width=1)

        # 감정선
        fig.add_trace(go.Scatter(
            x=df["날짜"],
            y=df["점수"],
            mode="lines+markers+text",
            line=dict(color="#9B72CF", width=2.5, shape="spline"),
            marker=dict(
                size=18,
                color=df["색상"],
                line=dict(color="#555", width=1),
            ),
            text=df["emoji"],
            textposition="top center",
            textfont=dict(size=16),
            hovertemplate="<b>%{x}</b><br>감정: %{customdata}<br>점수: %{y}<extra></extra>",
            customdata=df["감정"],
        ))

        fig.update_layout(
            title=f"{view_name} 감정 흐름 ({view_ym})",
            xaxis=dict(
                title="날짜·시간대",
                tickangle=-45,
                tickfont=dict(size=11),
                showgrid=True,
                gridcolor="#f0f0f0",
            ),
            yaxis=dict(
                title="감정 점수",
                range=[-5.8, 5.8],
                tickvals=[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
                ticktext=["−5 (화남)", "−4", "−3", "−2", "−1", "0", "+1", "+2", "+3", "+4", "+5 (행복)"],
                showgrid=True,
                gridcolor="#f0f0f0",
            ),
            height=430,
            margin=dict(l=20, r=20, t=60, b=80),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── 요약 카드 ──────────────────────────────────────────────────────────
        avg_score = df["점수"].mean()
        max_row   = df.loc[df["점수"].idxmax()]
        min_row   = df.loc[df["점수"].idxmin()]

        c1, c2, c3 = st.columns(3)
        c1.metric("평균 감정 점수", f"{avg_score:+.1f}")
        c2.metric("가장 좋았던 순간", f"{max_row['감정']}", f"{max_row['날짜']}")
        c3.metric("가장 힘든 순간",   f"{min_row['감정']}", f"{min_row['날짜']}")

        # ── 오전/오후 평균 비교 바 ─────────────────────────────────────────────
        st.markdown("#### 오전 vs 오후 평균 비교")
        am_scores = [r["점수"] for r in records if "오전" in r["날짜"]]
        pm_scores = [r["점수"] for r in records if "오후" in r["날짜"]]
        bar_df = pd.DataFrame({
            "시간대": ["오전", "오후"],
            "평균 점수": [
                round(sum(am_scores)/len(am_scores), 2) if am_scores else 0,
                round(sum(pm_scores)/len(pm_scores), 2) if pm_scores else 0,
            ],
        })
        bar_fig = px.bar(
            bar_df, x="시간대", y="평균 점수",
            color="시간대",
            color_discrete_map={"오전": "#FFB84C", "오후": "#7469B6"},
            text="평균 점수",
            range_y=[-5, 5],
        )
        bar_fig.update_traces(texttemplate="%{text:+.2f}", textposition="outside")
        bar_fig.update_layout(
            height=300, showlegend=False,
            yaxis=dict(zeroline=True, zerolinecolor="#aaa"),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        bar_fig.add_hline(y=0, line_dash="dot", line_color="#aaa")
        st.plotly_chart(bar_fig, use_container_width=True)

#############################################
# 3. 👥 오늘의 학급 감정 PAGE (선생님 전용)
#############################################
elif menu == "👥 오늘의 학급 감정":
    st.title("학급 정서 기록🧡")
    st.header("👥 오늘의 학급 감정 현황")
    st.caption(f"📅 {today_key} 기준 · 오전·오후 기록 현황")

    # ── 날짜 선택 ────────────────────────────────────────────────────────────
    view_date = st.date_input("날짜 선택", value=today, key="class_mood_date")
    view_year  = view_date.year
    view_month = view_date.month
    view_day   = view_date.day
    view_ym    = f"{view_year}-{str(view_month).zfill(2)}"

    # ── 학생별 오전/오후 감정 수집 ────────────────────────────────────────────
    rows = []
    for sname in STUDENT_LIST:
        day_dict = st.session_state.mood_data.get(sname, {}).get(view_ym, {}).get(view_day, {})
        am_idx = day_dict.get("오전") if isinstance(day_dict, dict) else None
        pm_idx = day_dict.get("오후") if isinstance(day_dict, dict) else None

        am_label = f"{EMOTIONS[am_idx][1]} {EMOTIONS[am_idx][0]}" if am_idx is not None else "—"
        pm_label = f"{EMOTIONS[pm_idx][1]} {EMOTIONS[pm_idx][0]}" if pm_idx is not None else "—"
        am_score = EMOTIONS[am_idx][3] if am_idx is not None else None
        pm_score = EMOTIONS[pm_idx][3] if pm_idx is not None else None
        am_color = EMOTIONS[am_idx][2] if am_idx is not None else "#f0f0f0"
        pm_color = EMOTIONS[pm_idx][2] if pm_idx is not None else "#f0f0f0"

        rows.append({
            "이름": sname,
            "오전_감정": am_label,
            "오전_점수": am_score,
            "오전_색": am_color,
            "오후_감정": pm_label,
            "오후_점수": pm_score,
            "오후_색": pm_color,
        })

    # ── 카드형 테이블 ─────────────────────────────────────────────────────────
    header_html = """
    <style>
    .class-table{width:100%;border-collapse:collapse;margin-top:8px;}
    .class-table th{background:#f5f0ff;color:#555;font-size:0.9em;padding:8px 6px;border-bottom:2px solid #ddd;text-align:center;}
    .class-table td{padding:7px 6px;border-bottom:1px solid #eee;text-align:center;font-size:0.95em;vertical-align:middle;}
    .emo-chip{display:inline-block;border-radius:20px;padding:3px 10px;font-weight:600;font-size:0.88em;color:#222;}
    .score-pos{color:#2ecc71;font-weight:bold;}
    .score-neg{color:#e74c3c;font-weight:bold;}
    .score-neu{color:#aaa;}
    </style>
    <table class='class-table'>
    <tr>
      <th>이름</th>
      <th>🌤 오전 감정</th>
      <th>점수</th>
      <th>🌆 오후 감정</th>
      <th>점수</th>
    </tr>
    """

    def score_html(s):
        if s is None: return "<span class='score-neu'>—</span>"
        cls = "score-pos" if s > 0 else ("score-neg" if s < 0 else "score-neu")
        return f"<span class='{cls}'>{'+' if s > 0 else ''}{s}</span>"

    body_html = ""
    for r in rows:
        am_bg   = r["오전_색"]
        pm_bg   = r["오후_색"]
        am_text = r["오전_감정"]
        pm_text = r["오후_감정"]
        am_chip = f"<span class='emo-chip' style='background:{am_bg};'>{am_text}</span>"
        pm_chip = f"<span class='emo-chip' style='background:{pm_bg};'>{pm_text}</span>"
        name    = r["이름"]
        body_html += (
            f"<tr>"
            f"<td><b>{name}</b></td>"
            f"<td>{am_chip}</td>"
            f"<td>{score_html(r['오전_점수'])}</td>"
            f"<td>{pm_chip}</td>"
            f"<td>{score_html(r['오후_점수'])}</td>"
            f"</tr>"
        )

    st.markdown(header_html + body_html + "</table>", unsafe_allow_html=True)

    # ── 학급 평균 점수 요약 ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 학급 평균 감정 점수")

    all_am = [r["오전_점수"] for r in rows if r["오전_점수"] is not None]
    all_pm = [r["오후_점수"] for r in rows if r["오후_점수"] is not None]
    all_scores = all_am + all_pm

    c1, c2, c3 = st.columns(3)
    c1.metric("오전 평균", f"{sum(all_am)/len(all_am):+.1f}" if all_am else "—")
    c2.metric("오후 평균", f"{sum(all_pm)/len(all_pm):+.1f}" if all_pm else "—")
    c3.metric("전체 평균", f"{sum(all_scores)/len(all_scores):+.1f}" if all_scores else "—")

    # ── 감정 분포 도넛 차트 (오전+오후 합산) ──────────────────────────────────
    emotion_counts = {}
    for r in rows:
        for key in ["오전_감정", "오후_감정"]:
            label = r[key]
            if label != "—":
                emotion_counts[label] = emotion_counts.get(label, 0) + 1

    if emotion_counts:
        st.markdown("#### 오늘 학급에서 가장 많이 느낀 감정")
        donut_labels = list(emotion_counts.keys())
        donut_values = list(emotion_counts.values())
        # 색상 매핑
        color_map = {f"{e[1]} {e[0]}": e[2] for e in EMOTIONS}
        donut_colors = [color_map.get(lb, "#ccc") for lb in donut_labels]

        donut_fig = go.Figure(go.Pie(
            labels=donut_labels,
            values=donut_values,
            hole=0.5,
            marker=dict(colors=donut_colors, line=dict(color="#fff", width=2)),
            textinfo="label+value",
            hovertemplate="%{label}<br>%{value}명<extra></extra>",
        ))
        donut_fig.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            paper_bgcolor="white",
        )
        st.plotly_chart(donut_fig, use_container_width=True)

    # ── 미기록 학생 안내 ──────────────────────────────────────────────────────
    unrecorded = [r["이름"] for r in rows if r["오전_감정"] == "—" and r["오후_감정"] == "—"]
    if unrecorded:
        st.warning(f"아직 오늘 감정을 기록하지 않은 학생: {', '.join(unrecorded)}")

#############################################
# 4. 🎁 오늘의 주인공 PAGE (월별 배정)
#############################################
elif menu == "🎁 오늘의 주인공":
    st.title("학급 정서 기록🧡")
    st.header("오늘의 주인공은?")

    current_student = st.session_state.logged_in_student

    # 오늘 주인공 (월별 배정표 기반)
    today_hero = get_today_hero(today)
    my_revealed = st.session_state.hero_revealed.get(current_student, {}).get(today_key, False)

    if current_student not in st.session_state.student_gift_opening:
        st.session_state.student_gift_opening[current_student] = False

    if my_revealed and today_hero:
        st.markdown(
            """
            <div style='text-align:center; margin: 40px 0;'>
                <div style='font-size:180px; margin-bottom:20px;'>🎉</div>
                <div style='font-size:48px; font-weight:bold; color:#e17055; margin-bottom:30px;'>{}</div>
            </div>
            <style>
            @keyframes rise {{
                0%   {{ transform: translateY(0) rotate(0deg); opacity: 1; }}
                100% {{ transform: translateY(-100vh) rotate(20deg); opacity: 0; }}
            }}
            .balloon {{
                position: fixed; bottom: -80px; font-size: 48px;
                animation: rise linear infinite; z-index: 9999; pointer-events: none;
            }}
            </style>
            <div class='balloon' style='left:5%;  animation-duration:3.2s; animation-delay:0.0s;'>🎈</div>
            <div class='balloon' style='left:15%; animation-duration:2.8s; animation-delay:0.3s;'>🎈</div>
            <div class='balloon' style='left:25%; animation-duration:3.5s; animation-delay:0.6s;'>🎊</div>
            <div class='balloon' style='left:35%; animation-duration:2.6s; animation-delay:0.1s;'>🎈</div>
            <div class='balloon' style='left:45%; animation-duration:3.0s; animation-delay:0.5s;'>🎊</div>
            <div class='balloon' style='left:55%; animation-duration:2.9s; animation-delay:0.2s;'>🎈</div>
            <div class='balloon' style='left:65%; animation-duration:3.3s; animation-delay:0.4s;'>🎊</div>
            <div class='balloon' style='left:75%; animation-duration:2.7s; animation-delay:0.7s;'>🎈</div>
            <div class='balloon' style='left:85%; animation-duration:3.1s; animation-delay:0.0s;'>🎊</div>
            <div class='balloon' style='left:93%; animation-duration:2.5s; animation-delay:0.3s;'>🎈</div>
            """.format(today_hero),
            unsafe_allow_html=True,
        )
        st.balloons()

    elif not st.session_state.student_gift_opening[current_student]:
        st.markdown(
            """
            <div style='text-align:center; margin: 80px 0;'>
                <div style='font-size:120px; display:inline-block;'>🎁</div>
                <div style='font-size:24px; color:#666; margin-top:60px; font-weight:bold;'>오늘의 주인공을 확인하세요!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            if st.button("🎈 오늘의 주인공 확인", key="open_gift", use_container_width=True):
                st.session_state.student_gift_opening[current_student] = True
                st.rerun()

    else:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(
                """
                <div style='text-align:center; margin: 60px 0;'>
                    <div style='font-size:200px; margin-bottom:20px;'>🥁</div>
                    <div style='font-size:32px; font-weight:bold; color:#e17055;'>두구두구두구두구….</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        time.sleep(1)
        placeholder.empty()

        if current_student not in st.session_state.hero_revealed:
            st.session_state.hero_revealed[current_student] = {}
        st.session_state.hero_revealed[current_student][today_key] = True
        st.balloons()
        st.rerun()

#############################################
# 5. 📅 이달의 배정표 PAGE (선생님 전용)
#############################################
elif menu == "📅 이달의 배정표":
    st.title("학급 정서 기록🧡")
    st.header("📅 이달의 주인공 배정표")

    current_student = st.session_state.logged_in_student
    if current_student != "선생님":
        st.warning("선생님 계정에서만 배정표를 확인할 수 있습니다.")
        st.stop()

    view_ym = st.selectbox(
        "월 선택",
        options=[f"{today.year}-{str(m).zfill(2)}" for m in range(1, 13)],
        index=today.month - 1,
        key="schedule_ym",
    )
    year, month = map(int, view_ym.split("-"))
    _, num_days = calendar.monthrange(year, month)
    schedule = get_hero_schedule(view_ym)

    rows = []
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        hero_idx = (day - 1) % len(schedule)
        rows.append({
            "날짜": d.strftime("%Y-%m-%d"),
            "요일": ["월", "화", "수", "목", "금", "토", "일"][d.weekday()],
            "오늘의 주인공": schedule[hero_idx],
        })

    df = pd.DataFrame(rows)
    # 주말 제외 여부 선택
    show_weekend = st.checkbox("주말 포함", value=False)
    if not show_weekend:
        df = df[~df["요일"].isin(["토", "일"])]

    st.dataframe(df, use_container_width=True, hide_index=True)

    # 재셔플 버튼
    st.markdown("---")
    st.caption("⚠️ 재셔플하면 이달 배정이 새로 바뀝니다.")
    if st.button("🔀 이 달 배정 다시 섞기", type="secondary"):
        shuffled = STUDENT_LIST.copy()
        random.shuffle(shuffled)
        st.session_state.hero_schedule[view_ym] = shuffled
        st.success("재셔플 완료!")
        st.rerun()

    # CSV 다운로드
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 배정표 CSV 다운로드",
        data=csv,
        file_name=f"hero_schedule_{view_ym}.csv",
        mime="text/csv",
        use_container_width=True,
    )

#############################################
# 6. 💌 오늘의 칭찬샤워 PAGE
#############################################
elif menu == "💌 오늘의 칭찬샤워":
    st.title("학급 정서 기록🧡")
    st.header("오늘의 칭찬샤워 💌")

    current_student = st.session_state.logged_in_student
    today_hero = st.session_state.hero_pick_history.get(today_key, None)
    hero_revealed = st.session_state.hero_revealed.get(current_student, {}).get(today_key, False)

    if not today_hero or not hero_revealed:
        st.warning("아직 오늘의 주인공이 공개되지 않았습니다! '오늘의 주인공' 탭에서 선물 상자를 열어주세요. 🎁")
    else:
        st.subheader(f"오늘의 주인공: {today_hero}")
        if today_key not in st.session_state.praise_shower:
            st.session_state.praise_shower[today_key] = []

        st.markdown("### 🎤 목소리 또는 타자로 칭찬 남기기")
        st.caption("마이크 버튼으로 말하면 자동으로 텍스트가 채워져요. 확인 후 등록 버튼을 누르세요!")

        import streamlit.components.v1 as components

        voice_html = f"""
        <div style="font-family:sans-serif;padding:4px 0;">
            <div style="display:flex;align-items:center;gap:12px;">
                <button id="mic-btn" type="button"
                    style="background:#ff7675;color:white;border:none;padding:10px 18px;
                           font-size:14px;border-radius:20px;cursor:pointer;font-weight:bold;">
                    🔴 마이크 켜고 말하기
                </button>
                <span id="status-msg" style="color:#888;font-size:13px;font-weight:bold;">
                    📝 말하면 아래 입력창에 자동으로 채워져요
                </span>
            </div>
        </div>
        <script>
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        const micBtn = document.getElementById('mic-btn');
        const statusMsg = document.getElementById('status-msg');
        if (!SR) {{
            statusMsg.innerText = "❌ 크롬/웨일 브라우저를 사용해주세요.";
            statusMsg.style.color = "#ff7675";
            micBtn.disabled = true; micBtn.style.background = "#ccc";
        }} else {{
            const rec = new SR();
            rec.lang = 'ko-KR';
            rec.interimResults = true;
            let finalText = '';
            micBtn.onclick = () => {{
                finalText = '';
                try {{ rec.start(); }} catch(e) {{}}
            }};
            rec.onstart = () => {{
                statusMsg.innerText = "🎤 말하는 중...";
                statusMsg.style.color = "#e17055";
                micBtn.innerText = "👂 듣고 있어요";
                micBtn.style.background = "#ffeaa7";
                micBtn.style.color = "#333";
            }};
            rec.onresult = (e) => {{
                let interim = '';
                for (let i = e.resultIndex; i < e.results.length; i++) {{
                    if (e.results[i].isFinal) {{ finalText += e.results[i][0].transcript; }}
                    else {{ interim = e.results[i][0].transcript; }}
                }}
                const textareas = window.parent.document.querySelectorAll('textarea');
                for (const ta of textareas) {{
                    if (ta.placeholder && ta.placeholder.includes('{today_hero}')) {{
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(ta, finalText + interim);
                        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        break;
                    }}
                }}
            }};
            rec.onend = () => {{
                statusMsg.innerText = "✅ 완료! 아래 내용을 확인 후 등록하세요.";
                statusMsg.style.color = "#2ecc71";
                micBtn.innerText = "🔴 마이크 켜고 말하기";
                micBtn.style.background = "#ff7675";
                micBtn.style.color = "white";
            }};
            rec.onerror = () => {{
                statusMsg.innerText = "❌ 마이크 권한을 허용해주세요.";
                statusMsg.style.color = "#ff7675";
                micBtn.innerText = "🔴 마이크 켜고 말하기";
                micBtn.style.background = "#ff7675";
                micBtn.style.color = "white";
            }};
        }}
        </script>
        """
        components.html(voice_html, height=60)

        praise_text = st.text_area(
            f"✏️ {today_hero}에게 하고 싶은 말",
            placeholder=f"{today_hero}에게 칭찬을 남겨주세요...",
            height=110,
            key="praise_input",
        )

        if st.button("💌 이 칭찬 전하기 (등록)", use_container_width=True, type="primary"):
            if praise_text and praise_text.strip():
                st.session_state.praise_shower[today_key].append((current_student, praise_text.strip()))
                st.success("🎉 칭찬이 등록되었습니다!")
                st.rerun()
            else:
                st.warning("칭찬 내용을 입력하거나 말해 주세요!")

        st.markdown("---")
        st.subheader("모두가 남긴 칭찬들 🌻")
        all_praises = st.session_state.praise_shower[today_key]

        if "editing_praise_idx" not in st.session_state: st.session_state.editing_praise_idx = None
        if "editing_praise_text" not in st.session_state: st.session_state.editing_praise_text = ""

        if not all_praises:
            st.caption("아직 등록된 칭찬이 없습니다. 첫 번째 칭찬을 남겨보세요!")
        else:
            for idx, item in enumerate(all_praises):
                writer, text = item if isinstance(item, tuple) else ("알 수 없음", item)
                col1, col2 = st.columns([8, 1])
                with col1:
                    if st.session_state.editing_praise_idx == idx:
                        new_text = st.text_area(f"칭찬 수정 ({idx+1})", value=st.session_state.editing_praise_text, key=f"edit_{idx}")
                        if st.button("저장", key=f"save_{idx}"):
                            if new_text.strip():
                                st.session_state.praise_shower[today_key][idx] = (writer, new_text.strip())
                                st.session_state.editing_praise_idx = None
                                st.session_state.editing_praise_text = ""
                                st.success("칭찬이 수정되었습니다!")
                                st.rerun()
                            else:
                                st.warning("수정할 내용을 입력하세요.")
                        if st.button("취소", key=f"cancel_{idx}"):
                            st.session_state.editing_praise_idx = None
                            st.session_state.editing_praise_text = ""
                            st.rerun()
                    else:
                        st.info(f"{idx+1}. {text} (작성자: {writer})")
                with col2:
                    if st.session_state.editing_praise_idx != idx:
                        if st.button("수정", key=f"editbtn_{idx}"):
                            st.session_state.editing_praise_idx = idx
                            st.session_state.editing_praise_text = text
                            st.rerun()

        if all_praises and current_student == "선생님":
            rows = [(item[0], item[1]) if isinstance(item, tuple) else ("알 수 없음", item) for item in all_praises]
            praise_df = pd.DataFrame({
                "주인공": [today_hero] * len(rows),
                "날짜":   [today_key]  * len(rows),
                "작성자": [r[0] for r in rows],
                "칭찬":   [r[1] for r in rows],
            })
            csv = praise_df.to_csv(index=False).encode("utf-8-sig")
            st.write("")
            st.download_button(
                "칭찬샤워 엑셀로 다운로드 📥",
                data=csv,
                file_name=f"praise_{today_key}.csv",
                mime="text/csv",
                use_container_width=True,
            )
