import streamlit as st
from datetime import datetime
import os
import requests
from pytz import timezone
from dotenv import load_dotenv
import db_update
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from io import BytesIO
import numpy as np
import pandas as pd
import sqlite3
from streamlit_gsheets import GSheetsConnection

conn_gsheets = st.connection("gsheets", type=GSheetsConnection)

def load_user_data(email):
    try:
        df = conn_gsheets.read(ttl=0)
        if df.empty or 'email' not in df.columns:
            return None
        user_df = df[df['email'] == email]
        if not user_df.empty:
            row = user_df.iloc[0].to_dict()
            return [
                row.get('email'),
                str(row.get('grade', '1')),
                str(row.get('class_nm', '1')),
                row.get('sel_A', ''), row.get('sel_B', ''), row.get('sel_C', ''), row.get('sel_D', ''),
                row.get('sel_E', ''), row.get('sel_F', ''), row.get('sel_G', ''), row.get('sel_H', ''),
                int(row.get('dark_mode', 0)) if pd.notna(row.get('dark_mode')) else 0
            ]
    except Exception as e:
        st.error(f"구글 시트 로드 실패: {e}")
        return None

def save_user_data(email, grade, class_nm, sel_dict, dark_mode):
    try:
        try:
            df = conn_gsheets.read(ttl=0)
        except:
            df = pd.DataFrame()

        columns = ['email', 'grade', 'class_nm', 'sel_A', 'sel_B', 'sel_C', 'sel_D', 'sel_E', 'sel_F', 'sel_G', 'sel_H', 'dark_mode']
        if df.empty or 'email' not in df.columns:
            df = pd.DataFrame(columns=columns)

        dm_val = 1 if dark_mode else 0
        new_row = {
            'email': email, 'grade': str(grade), 'class_nm': str(class_nm),
            'sel_A': sel_dict.get('선택 A', ''), 'sel_B': sel_dict.get('선택 B', ''),
            'sel_C': sel_dict.get('선택 C', ''), 'sel_D': sel_dict.get('선택 D', ''),
            'sel_E': sel_dict.get('선택 E', ''), 'sel_F': sel_dict.get('선택 F', ''),
            'sel_G': sel_dict.get('선택 G', ''), 'sel_H': sel_dict.get('선택 H', ''),
            'dark_mode': dm_val
        }

        if email in df['email'].values:
            idx = df[df['email'] == email].index[0]
            for col, val in new_row.items():
                df.at[idx, col] = val
        else:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        conn_gsheets.update(data=df)
    except Exception as e:
        st.error(f"구글 시트 저장 실패: {e}")

default_dark = False
default_grade = "1"
default_class = "1"
saved_sel = {f'선택 {i}': '' for i in 'ABCDEFGH'}

if st.user.is_logged_in:
    user_row = load_user_data(st.user.email)
    if user_row:
        default_grade = user_row[1]
        default_class = user_row[2]
        for idx, key in enumerate('ABCDEFGH'):
            saved_sel[f'선택 {key}'] = user_row[3 + idx]
        if len(user_row) > 11 and user_row[11] is not None:
            default_dark = True if user_row[11] == 1 else False

grades_list = ["1", "2", "3"]
classes_list = [str(i) for i in range(1, 10)]
grade_idx = grades_list.index(default_grade) if default_grade in grades_list else 0
class_idx = classes_list.index(default_class) if default_class in classes_list else 0

with st.sidebar:
    st.title("사용자 인증")
    if not st.user.is_logged_in:
        st.button("구글 로그인", on_click=st.login, args=["google"])
    else:
        st.write(f"**{st.user.name}**님")
        st.write(f"({st.user.email})")
        if st.button("로그아웃"):
            st.logout()
            st.stop()

st.title('대건고등학교')

today = st.date_input("조회일", value=datetime.now(timezone('Asia/Seoul')))
today_str = today.strftime("%Y%m%d")

load_dotenv()
API_KEY = os.getenv("NEIS_KEY") or st.secrets["NEIS_KEY"]
DINNER_KEY = os.getenv("DINNER_KEY") or st.secrets["DINNER_KEY"]
ATPT_OFCDC_SC_CODE = 'D10'
SD_SCHUL_CODE = '7240082'

allergyinfo = '--- \n\n #### 알러지 정보 \n\n ①난류(가금류) ②우유 ③메밀 ④땅콩 ⑤대두 ⑥밀 ⑦고등어 ⑧게 ⑨새우 ⑩돼지고기 ⑪복숭아 \n\n ⑫토마토 ⑬아황산염 ⑭호두 ⑮닭고기 ⑯쇠고기 ⑰오징어 ⑱조개류(전복, 홍합포함) ⑲잣'

tab1, tab2, tab3 = st.tabs(["중식", "석식", "시간표"])

with tab1:
    st.markdown("## 중식 식단")
    url = 'https://open.neis.go.kr/hub/mealServiceDietInfo'
    params = {'KEY': API_KEY, 'Type': 'json', 'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE, 'SD_SCHUL_CODE': SD_SCHUL_CODE, 'MLSV_YMD': today_str}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        meals = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
        cleaned = meals.replace('<br/>', '\n')
        for item in cleaned.strip().split('\n'):
            st.markdown(f"- {item.strip()}")
    except:
        st.error("중식 정보가 없습니다.")
    st.markdown(allergyinfo)

with tab3:
    st.title('시간표 생성기')
    
    if not st.user.is_logged_in:
        st.info("💡 로그인하면 학년, 반, 선택과목 정보를 저장해둘 수 있습니다.")

    is_dark = st.toggle("🌙 다크 모드", value=default_dark)

    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("학년", grades_list, index=grade_idx)
    with col2:
        class_nm = st.selectbox("반", classes_list, index=class_idx)
    
    code1 = float(f'{grade}0{class_nm}1')

    try:
        df = pd.read_excel('Timetable_all_raw_v2.xlsx', header=None)
        raw = df.loc[df[0] == code1, 2:36].iloc[0]
    except:
        st.error("엑셀 파일에서 해당 반의 시간표 데이터를 찾을 수 없습니다.")
        st.stop()

    dic = {}
    elective = set()
    if grade != '1':
        st.markdown("#### 선택과목 입력")
        cols1 = st.columns(4)
        cols2 = st.columns(4)
        all_cols = cols1 + cols2
        for idx, i in enumerate('ABCDEFGH'):
            with all_cols[idx]:
                dic[f'선택 {i}'] = st.text_input(f'선택 {i}', value=saved_sel[f'선택 {i}'])
                elective.add(f'선택 {i}')
        raw = raw.tolist()
        for i in range(35):
            if str(raw[i]) in elective:
                raw[i] = dic[str(raw[i])]

    if st.user.is_logged_in:
        if st.button("💾 내 정보 저장"):
            save_user_data(st.user.email, grade, class_nm, dic, is_dark)
            st.toast("내 정보가 성공적으로 저장되었습니다!")

    result = np.array(raw).reshape(-1,7).T

    def create_timetable_image(data_array, dark_mode=False):
        days = ['월', '화', '수', '목', '금']
        periods = [f'{i}교시' for i in range(1, 8)]
        df_tt = pd.DataFrame(data_array, columns=days, index=periods)

        bg_color = '#101116' if dark_mode else '#ffffff'
        text_color = '#ffffff' if dark_mode else '#000000'
        header_color = '#27272F' if dark_mode else '#F1F2F6'
        grid_color = '#bbbbbb' if dark_mode else '#333333' 

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor(bg_color)
        ax.axis('off')

        fe = fm.FontEntry(fname='./경기천년체/경기천년바탕_Bold.ttf', name='경기')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rc('font', family='경기')

        table = ax.table(
            cellText=df_tt.values,
            colLabels=df_tt.columns,
            rowLabels=df_tt.index,
            cellLoc='center',
            loc='center',
            colColours=[header_color] * 5,
            rowColours=[header_color] * 7
        )

        table.auto_set_font_size(True)
        table.scale(1, 4)

        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor(grid_color)
            cell.set_linewidth(1.5)
            cell.get_text().set_color(text_color)
            if row == 0 or col == -1:
                cell.set_facecolor(header_color)
                cell.get_text().set_weight('bold')
            else:
                cell.set_facecolor(bg_color)

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', dpi=300, facecolor=bg_color)
        buf.seek(0)
        plt.close(fig)
        return buf

    st.markdown('---')
    try:
        img_buf = create_timetable_image(result, dark_mode=is_dark)
        st.write("### 🕒 완성된 시간표")
        st.image(img_buf) 
        st.download_button(label="이미지 다운로드", data=img_buf, file_name="timetable.png", mime="image/png")
    except Exception as e:
        st.error(f"시간표 생성 실패: {e}")

with tab2:
    st.markdown("## 석식 식단")
    DB_PATH = "dinner_menu.db"
    def load_from_db(date):
        if not os.path.exists(DB_PATH): return None
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT menu FROM dinner WHERE date = ?", (date,))
            row = cur.fetchone()
            conn.close()
            return row[0].split("\n") if row else None
        except: return None

    meals = load_from_db(today_str)
    if not meals:
        with st.spinner("API 호출 중..."):
            if db_update.update_db(DB_PATH, today_str, DINNER_KEY):
                meals = load_from_db(today_str)
        if not meals: 
            st.error("석식 정보를 찾을 수 없습니다.")
    else:
        for item in meals: st.markdown(f"- {item}")
    st.markdown(allergyinfo)
