import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# アプリの基本設定
st.set_page_config(page_title="Jibun-Flow", page_icon="📱", layout="centered")

# --- デザイン（LINE風スタイル） ---
st.markdown("""
<style>
.stApp { background-color: #7494C4; } 
.stChatMessage { border-radius: 15px; padding: 10px; margin: 5px 0; }
.stTable { background-color: white; border-radius: 10px; }
[data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.title("📱 Jibun-Flow")

# --- 1. 日付と基本設定 ---
selected_date = st.date_input("日付を選択", datetime.now())
st.caption(f"{selected_date.strftime('%Y年%m月%d日')} のスケジュール")

# 固定ルーティン（7:00起床、7:00-7:30朝食）
routines = [
    {"予定": "起床・朝食", "開始": "07:00", "終了": "07:30"},
    {"予定": "昼食", "開始": "12:00", "終了": "13:00"},
    {"予定": "夕食", "開始": "18:00", "終了": "18:30"},
]

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- 2. タスク入力機能 ---
st.chat_message("assistant").write("7:30以降の予定を教えてください。")

with st.container():
    task_input = st.text_input("何をする？", key="new_task_name", placeholder="例：数学の勉強")
    duration_input = st.number_input("時間(分)", min_value=15, step=15, value=60)
    t_type = st.radio("優先度", ["必須(Must)", "希望(Want)"], horizontal=True)

    if st.button("予定を追加"):
        if task_input:
            priority = 1 if t_type == "必須(Must)" else 2
            st.session_state.tasks.append({"内容": task_input, "分": duration_input, "優先": priority})
            st.success(f"「{task_input}」を追加しました")

# --- 3. スケジュール計算ロジック ---
def generate_schedule(tasks):
    current_time = datetime.strptime("07:00", "%H:%M")
    end_of_day = datetime.strptime("23:30", "%H:%M")
    tasks_sorted = sorted(tasks, key=lambda x: x['優先'])
    full_schedule = []

    while current_time < end_of_day:
        t_str = current_time.strftime("%H:%M")
        
        # 固定ルーティンの判定
        r = next((x for x in routines if x['開始'] <= t_str < x['終了']), None)
        
        if r:
            r_end = datetime.strptime(r['終了'], "%H:%M")
            full_schedule.append({"時刻": f"{t_str} - {r['終了']}", "予定": r['予定'], "区分": "🏠"})
            current_time = r_end
        elif tasks_sorted:
            task = tasks_sorted.pop(0)
            end_t = current_time + timedelta(minutes=task['分'])
            full_schedule.append({"時刻": f"{t_str} - {end_t.strftime('%H:%M')}", "予定": task['内容'], "区分": "📝"})
            current_time = end_t
        else:
            full_schedule.append({"時刻": f"{t_str} - {(current_time + timedelta(minutes=30)).strftime('%H:%M')}", "予定": "自由時間", "区分": "☕"})
            current_time += timedelta(minutes=30)
            
    return pd.DataFrame(full_schedule)

# --- 4. 表示（午前・午後切り替えボタン） ---
if st.session_state.tasks or True:
    st.markdown("---")
    view_mode = st.radio("表示範囲", ["午前 (7:00-12:00)", "午後 (12:00-23:30)", "一日中"], horizontal=True)
    
    df = generate_schedule(st.session_state.tasks.copy())
    
    # フィルタリング
    if view_mode == "午前 (7:00-12:00)":
        df = df[df['時刻'].str.contains('^07|^08|^09|^10|^11')]
    elif view_mode == "午後 (12:00-23:30)":
        df = df[~df['時刻'].str.contains('^07|^08|^09|^10|^11')]

    st.table(df)

    if st.button("予定をリセット"):
        st.session_state.tasks = []
        st.rerun()
