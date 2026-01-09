import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. アプリの基本設定
st.set_page_config(page_title="Jibun-Flow", page_icon="📱", layout="centered")

# --- 2. デザイン（視認性を最優先：文字色を黒に固定） ---
st.markdown("""
<style>
    /* 全体の背景色（LINE風の水色） */
    .stApp { background-color: #7494C4; }
    
    /* 文字の色をすべて濃いネイビー（#1E1E1E）に固定 */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #1E1E1E !important;
    }
    
    /* 入力欄のラベルを見やすく */
    .stTextInput label, .stNumberInput label, .stRadio label {
        color: #1E1E1E !important;
        font-weight: bold !important;
    }
    
    /* スケジュール表（テーブル）のスタイル */
    .stTable { 
        background-color: white !important; 
        border-radius: 10px; 
    }
    
    /* テーブル内の文字色も黒に固定 */
    .stTable td, .stTable th {
        color: #1E1E1E !important;
    }

    /* ラジオボタンや入力枠の背景を白に */
    div[data-baseweb="input"] {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📱 Jibun-Flow")

# --- 3. 日付と基本設定 ---
selected_date = st.date_input("日付を選択", datetime.now())
st.write(f"### {selected_date.strftime('%Y年%m月%d日')} の計画")

# 固定ルーティン（07:00-07:30 朝食）
routines = [
    {"予定": "起床・朝食", "開始": "07:00", "終了": "07:30"},
    {"予定": "昼食", "開始": "12:00", "終了": "13:00"},
    {"予定": "夕食", "開始": "18:00", "終了": "18:30"},
]

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- 4. タスク入力機能 ---
st.markdown("#### 📝 7:30以降の予定を追加")
with st.container():
    task_input = st.text_input("何をする？", key="new_task_name", placeholder="例：プログラミング学習")
    duration_input = st.number_input("所要時間（分）", min_value=15, step=15, value=60)
    t_type = st.radio("優先度", ["必須(Must)", "希望(Want)"], horizontal=True)

    if st.button("予定をリストに追加"):
        if task_input:
            priority = 1 if t_type == "必須(Must)" else 2
            st.session_state.tasks.append({"内容": task_input, "分": duration_input, "優先": priority})
            st.success(f"「{task_input}」を読み込みました。下の表を確認してください。")

# --- 5. スケジュール計算ロジック ---
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
            full_schedule.append({"時刻": f"{t_str} - {r['終了']}", "予定": r['予定'], "区分": "🏠 固定"})
            current_time = r_end
        elif tasks_sorted:
            task = tasks_sorted.pop(0)
            end_t = current_time + timedelta(minutes=task['分'])
            full_schedule.append({"時刻": f"{t_str} - {end_t.strftime('%H:%M')}", "予定": task['内容'], "区分": "📝 予定"})
            current_time = end_t
        else:
            # 何もない時間は自由時間
            next_event_time = end_of_day
            full_schedule.append({"時刻": f"{t_str} - {next_event_time.strftime('%H:%M')}", "予定": "自由時間", "区分": "☕"})
            break
            
    return pd.DataFrame(full_schedule)

# --- 6. 表示（午前・午後切り替え） ---
st.markdown("---")
view_mode = st.radio("表示する時間帯を選んでください", ["午前 (7時~)", "午後 (12時~)", "一日中"], horizontal=True)

df = generate_schedule(st.session_state.tasks.copy())

# フィルタリング処理（文字で見分ける）
if view_mode == "午前 (7時~)":
    df = df[df['時刻'].str.contains('^07|^08|^09|^10|^11')]
elif view_mode == "午後 (12時~)":
    df = df[~df['時刻'].str.contains('^07|^08|^09|^10|^11')]

# 表の表示
st.table(df)

if st.button("すべての予定をクリア"):
    st.session_state.tasks = []
    st.rerun()
