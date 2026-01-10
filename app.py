import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- アプリ名設定 ---
APP_NAME = "Focus" 

st.set_page_config(page_title=APP_NAME, page_icon="🎯", layout="centered")

# --- UIデザイン: ダークモードでも白飛びしない、黒文字・グレー背景の洗練されたUI ---
st.markdown(f"""
<style>
    /* 全体の背景色を洗練されたライトグレーに */
    .stApp {{ background-color: #F8F9FA !important; }} 
    
    /* すべての文字を「真っ黒」ではなく、目に優しい「深い黒」に固定 */
    h1, h2, h3, p, span, label, div, .stMarkdown, .stTable {{
        color: #1A1A1B !important;
    }}
    
    /* 入力欄（テキスト・数字）の背景を白に固定 */
    div[data-baseweb="input"], div[data-baseweb="number-input"] {{
        background-color: white !important;
        border-radius: 8px !important;
    }}

    /* スケジュール表（テーブル）のデザイン */
    .stTable {{ 
        background-color: white !important; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-top: 20px;
    }}
    .stTable td, .stTable th {{
        color: #1A1A1B !important;
        background-color: white !important;
        padding: 12px !important;
    }}

    /* ボタンのデザイン */
    .stButton>button {{
        border-radius: 20px !important;
        background-color: white !important;
        color: #1A1A1B !important;
        border: 1px solid #D1D5DB !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title(f"🎯 {APP_NAME}")

# --- 1. 日付指定 ---
selected_date = st.date_input("Select Date", datetime.now())
st.write(f"### {selected_date.strftime('%Y/%m/%d')} Plan")

# --- 2. 固定ルーティン設定 (07:00 起床・朝食を完全固定) ---
routines = [
    {"Task": "Breakfast", "Start": "07:00", "End": "07:30", "Icon": "☕"},
    {"Task": "Lunch", "Start": "12:00", "End": "13:00", "Icon": "🍴"},
    {"Task": "Dinner", "Start": "18:00", "End": "18:30", "Icon": "🌙"},
]

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- 3. タスク入力セクション ---
st.markdown("---")
with st.expander("＋ Add New Schedule (From 07:30)", expanded=True):
    t_name = st.text_input("What to do?", placeholder="Ex: Math, Programming...")
    t_mins = st.number_input("Duration (Minutes)", min_value=15, step=15, value=60)
    t_prio = st.radio("Priority", ["Must", "Want"], horizontal=True)
    
    if st.button("Add to List"):
        if t_name:
            prio_val = 1 if t_prio == "Must" else 2
            st.session_state.tasks.append({"name": t_name, "mins": t_mins, "prio": prio_val})
            st.rerun()

# --- 4. 自動スケジューリング計算 ---
def build_schedule(tasks):
    curr = datetime.strptime("07:00", "%H:%M")
    limit = datetime.strptime("23:30", "%H:%M")
    ts = sorted(tasks, key=lambda x: x['prio'])
    res = []

    while curr < limit:
        t_str = curr.strftime("%H:%M")
        # 固定ルーティンの判定
        r = next((x for x in routines if x['Start'] <= t_str < x['End']), None)
        
        if r:
            r_end = datetime.strptime(r['End'], "%H:%M")
            res.append({"Time": f"{t_str}-{r['End']}", "Activity": r['Task'], "Tag": r['Icon']})
            curr = r_end
        elif ts:
            task = ts.pop(0)
            end_v = curr + timedelta(minutes=task['mins'])
            res.append({"Time": f"{t_str}-{end_v.strftime('%H:%M')}", "Activity": task['name'], "Tag": "●"})
            curr = end_v
        else:
            # 何もない時間は自由時間
            res.append({"Time": f"{t_str}-{(curr + timedelta(minutes=30)).strftime('%H:%M')}", "Activity": "Free", "Tag": "○"})
            curr += timedelta(minutes=30)
            
    return pd.DataFrame(res)

# --- 5. 表示切り替えとテーブル表示 ---
st.markdown("---")
view_mode = st.radio("Display Range", ["Morning (7-12)", "Afternoon (12-23)", "All Day"], horizontal=True)

df = build_schedule(st.session_state.tasks.copy())

# フィルタリング
if view_mode == "Morning (7-12)":
    df = df[df['Time'].str.startswith(('07', '08', '09', '10', '11'))]
elif view_mode == "Afternoon (12-23)":
    df = df[~df['Time'].str.startswith(('07', '08', '09', '10', '11'))]

st.table(df)

# リセットボタン
if st.button("Reset All Tasks"):
    st.session_state.tasks = []
    st.rerun()
