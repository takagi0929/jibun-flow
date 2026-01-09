import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# アプリの基本設定
st.set_page_config(page_title="Jibun-Flow", page_icon="📱", layout="centered")

# --- デザイン ---
st.markdown("""
    <style>
    .stApp { background-color: #7494C4; } 
    .stChatMessage { border-radius: 15px; padding: 10px; margin: 5px 0; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📱 Jibun-Flow")
st.caption("AIがあなたの24時間をデザインします")

# 1. ルーティン設定
routines = [
    {"予定": "朝食", "開始": "07:30", "終了": "08:15"},
    {"予定": "昼食", "開始": "12:00", "終了": "13:00"},
    {"予定": "夕食", "開始": "18:00", "終了": "18:30"},
]

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- 2. 入力機能 ---
st.chat_message("assistant").write("今日は何をしますか？予定と時間を教えてください。")

with st.container():
    task_input = st.text_input("何をする？", key="new_task_name")
    duration_input = st.number_input("時間(分)", min_value=15, step=15, value=60)
    t_type = st.radio("優先度", ["やるべき(Must)", "やりたい(Want)"], horizontal=True)

    if st.button("送信"):
        if task_input:
            priority = 1 if t_type == "やるべき(Must)" else 2
            st.session_state.tasks.append({"予定": task_input, "時間": duration_input, "優先": priority})
            st.rerun()

# --- 3. 計算ロジック ---
def generate_schedule(tasks):
    current_time = datetime.strptime("07:00", "%H:%M")
    end_of_day = datetime.strptime("23:30", "%H:%M")
    tasks_sorted = sorted(tasks, key=lambda x: x['優先'])
    full_schedule = []

    while current_time < end_of_day:
        t_str = current_time.strftime("%H:%M")
        r = next((x for x in routines if x['開始'] <= t_str < x['終了']), None)
        if r:
            full_schedule.append({"時間": f"{r['開始']}-{r['終了']}", "内容": r['予定'], "タイプ": "🍱"})
            current_time = datetime.strptime(r['終了'], "%H:%M")
        elif tasks_sorted:
            task = tasks_sorted.pop(0)
            end_t = current_time + timedelta(minutes=task['時間'])
            full_schedule.append({"時間": f"{t_str}-{end_t.strftime('%H:%M')}", "内容": task['予定'], "タイプ": "✅"})
            current_time = end_t
        else:
            current_time += timedelta(minutes=15)
    return pd.DataFrame(full_schedule)

# --- 4. 表示 ---
if st.session_state.tasks:
    st.markdown("### 📅 本日のタイムライン")
    df = generate_schedule(st.session_state.tasks.copy())
    st.table(df)
    if st.button("リセット"):
        st.session_state.tasks = []
        st.rerun()
