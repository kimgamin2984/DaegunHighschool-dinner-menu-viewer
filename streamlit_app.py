# import sqlite3
# import streamlit as st
# from datetime import datetime
# import os
# import requests
# from pytz import timezone
# from dotenv import load_dotenv
# import db_update
# import streamlit as st
# import matplotlib.pyplot as plt
# import matplotlib.font_manager as fm
# from io import BytesIO
# import numpy as np
# import pandas as pd

# USER_DB_PATH = "user_data.db"

# def init_user_db():
#     conn = sqlite3.connect(USER_DB_PATH)
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS user_electives (
#             email TEXT PRIMARY KEY,
#             grade TEXT,
#             class_nm TEXT,
#             sel_A TEXT, sel_B TEXT, sel_C TEXT, sel_D TEXT,
#             sel_E TEXT, sel_F TEXT, sel_G TEXT, sel_H TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def load_user_data(email):
#     conn = sqlite3.connect(USER_DB_PATH)
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM user_electives WHERE email = ?", (email,))
#     row = cur.fetchone()
#     conn.close()
#     return row

# def save_user_data(email, grade, class_nm, sel_dict):
#     conn = sqlite3.connect(USER_DB_PATH)
#     conn.execute('''
#         INSERT OR REPLACE INTO user_electives
#         (email, grade, class_nm, sel_A, sel_B, sel_C, sel_D, sel_E, sel_F, sel_G, sel_H)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         email, grade, class_nm,
#         sel_dict.get('선택A', ''), sel_dict.get('선택B', ''), 
#         sel_dict.get('선택C', ''), sel_dict.get('선택D', ''), 
#         sel_dict.get('선택E', ''), sel_dict.get('선택F', ''), 
#         sel_dict.get('선택G', ''), sel_dict.get('선택H', '')
#     ))
#     conn.commit()
#     conn.close()

# init_user_db()

# with st.sidebar:
#     st.title("사용자 인증")
#     if not st.user.is_logged_in:
#         st.button("구글 로그인", on_click=st.login)
#     else:
#         st.write(f"**{st.user.name}**님")
#         st.write(f"({st.user.email})")
#         st.button("로그아웃", on_click=st.logout)

# st.title('대건고등학교')

# today = st.date_input("조회일", value=datetime.now(timezone('Asia/Seoul')))
# month = today.month
# day = today.day
# date_str = f"{month:02}월 {day:02}일"
# today_str = today.strftime("%Y%m%d")

# filename = os.path.join("menu", f"{today.year}{today.month:02}.pdf")
# load_dotenv()
# API_KEY = os.getenv("NEIS_KEY") or st.secrets["NEIS_KEY"]
# DINNER_KEY = os.getenv("DINNER_KEY") or st.secrets["DINNER_KEY"]
# ATPT_OFCDC_SC_CODE = 'D10'
# SD_SCHUL_CODE = '7240082'

# allergyinfo = '--- \n\n #### 알러지 정보 \n\n ①난류(가금류) ②우유 ③메밀 ④땅콩 ⑤대두 ⑥밀 ⑦고등어 ⑧게 ⑨새우 ⑩돼지고기 ⑪복숭아 \n\n ⑫토마토 ⑬아황산염 ⑭호두 ⑮닭고기 ⑯쇠고기 ⑰오징어 ⑱조개류(전복, 홍합포함) ⑲잣'

# tab1, tab2, tab3 = st.tabs(["중식", "석식", "시간표"])

# with tab1:
#     st.markdown("## 중식 식단")
#     url = 'https://open.neis.go.kr/hub/mealServiceDietInfo'
#     params = {
#         'KEY': API_KEY,
#         'Type': 'json',
#         'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
#         'SD_SCHUL_CODE': SD_SCHUL_CODE,
#         'MLSV_YMD': today_str
#     }
#     try:
#         res = requests.get(url, params=params)
#         data = res.json()
#         meals = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
#         cleaned = meals.replace('<br/>', '\n')
#         for item in cleaned.strip().split('\n'):
#             st.markdown(f"- {item.strip()}")
#     except:
#         st.error("중식 정보가 없습니다.")

#     st.markdown(allergyinfo)

# with tab3:
#     st.title('시간표 생성기')
#     default_grade = "1"
#     default_class = "1"
#     saved_sel = {f'선택 {i}': '' for i in 'ABCDEFGH'}

#     if st.user.is_logged_in:
#         user_row = load_user_data(st.user.email)
#         if user_row:
#             default_grade = user_row[1]
#             default_class = user_row[2]
#             for idx, key in enumerate('ABCDEFGH'):
#                 saved_sel[f'선택{key}'] = user_row[3 + idx]
#     else:
#         st.info("💡 로그인하면 학년, 반, 선택과목 정보를 저장해둘 수 있습니다.")

#     elective = set()
    
#     grades_list = ["1", "2", "3"]
#     classes_list = [str(i) for i in range(1, 10)]
    
#     grade_idx = grades_list.index(default_grade) if default_grade in grades_list else 0
#     class_idx = classes_list.index(default_class) if default_class in classes_list else 0

#     col1, col2 = st.columns(2)
#     with col1:
#         grade = st.selectbox("학년", grades_list, index=grade_idx)
#     with col2:
#         class_nm = st.selectbox("반", classes_list, index=class_idx)
        
#     code1 = float(f'{grade}0{class_nm}1')

#     try:
#         df = pd.read_excel('Timetable_all_raw_v2.xlsx', header=None)
#         raw = df.loc[df[0] == code1, 2:36].iloc[0]
#     except Exception as e:
#         st.error("엑셀 파일에서 해당 반의 시간표 데이터를 찾을 수 없습니다.")
#         st.stop()

#     dic = {}
#     if grade != '1':
#         st.markdown("#### 선택과목 입력")
#         cols1 = st.columns(4)
#         cols2 = st.columns(4)
#         all_cols = cols1 + cols2
        
#         for idx, i in enumerate('ABCDEFGH'):
#             with all_cols[idx]:
#                 dic[f'선택 {i}'] = st.text_input(f'선택 {i}', value=saved_sel[f'선택 {i}'])
#                 elective.add(f'선택 {i}')
        
#         raw = raw.tolist()
#         for i in range(35):
#             if raw[i] in elective:
#                 raw[i] = dic[raw[i]]

#     if st.user.is_logged_in:
#         if st.button("💾 내 학급/선택과목 정보 저장"):
#             save_user_data(st.user.email, grade, class_nm, dic)
#             st.success("내 정보가 성공적으로 저장되었습니다! 다음번 접속 시 자동으로 불러옵니다.")

#     result = np.array(raw).reshape(-1,7).T

#     def create_timetable_image(data_array):
#         days = ['월', '화', '수', '목', '금']
#         periods = [f'{i}교시' for i in range(1, 8)]

#         df_tt = pd.DataFrame(data_array, columns=days, index=periods)

#         fig, ax = plt.subplots(figsize=(10, 8))
#         ax.axis('off')

#         fe = fm.FontEntry(fname='./경기천년체/경기천년바탕_Bold.ttf', name='경기')
#         fm.fontManager.ttflist.insert(0,fe)
#         plt.rc('font', family='경기')
#         plt.rcParams['axes.unicode_minus'] = False 

#         table = ax.table(
#             cellText=df_tt.values,
#             colLabels=df_tt.columns,
#             rowLabels=df_tt.index,
#             cellLoc='center',
#             loc='center',
#             colColours=['#f2f2f2'] * 5,  
#             rowColours=['#f2f2f2'] * 7   
#         )

#         table.auto_set_font_size(True)
#         table.scale(1, 4)

#         buf = BytesIO()
#         plt.savefig(buf, format="png", bbox_inches='tight', dpi=300)
#         buf.seek(0)
#         plt.close(fig)
#         return buf

#     st.markdown('---')

#     try:
#         img_buf = create_timetable_image(result)
        
#         st.write("### 🕒 완성된 시간표")
#         st.image(img_buf) 

#         st.download_button(
#             label="다운로드",
#             data=img_buf,
#             file_name="timetable.png",
#             mime="image/png"
#         )
#     except Exception as e:
#         st.error(f"시간표 생성 실패: {e}")

# with tab2:
#     st.markdown("## 석식 식단")

#     DB_PATH = "dinner_menu.db"

#     msg = st.empty()

#     def load_from_db(date):
#         import sqlite3
#         if not os.path.exists(DB_PATH):
#             return None
#         try:
#             conn = sqlite3.connect(DB_PATH)
#             cur = conn.cursor()
#             cur.execute("SELECT menu FROM dinner WHERE date = ?", (date,))
#             row = cur.fetchone()
#             conn.close()
#             if row:
#                 return row[0].split("\n")
#         except:
#             pass
#         return None

#     meals = load_from_db(today_str)

#     if not meals:
#         msg.info("API 호출 중...")

#         try:
#             ok = db_update.update_db(DB_PATH, today_str, DINNER_KEY)

#             if ok:
#                 meals = load_from_db(today_str)
#                 msg.empty()
#             else:
#                 msg.empty()
#         except Exception as e:
#             msg.empty()
#             st.error("DB 업데이트 중 오류 발생")
#             st.error(e)

#     else:
#         msg.empty()

#     if not meals:
#         st.error("석식 정보를 찾을 수 없습니다.")
#     else:
#         for item in meals:
#             st.markdown(f"- {item}")

#     st.markdown(allergyinfo)

import sqlite3
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

USER_DB_PATH = "user_data.db"

def init_user_db():
    conn = sqlite3.connect(USER_DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_electives (
            email TEXT PRIMARY KEY,
            grade TEXT,
            class_nm TEXT,
            sel_A TEXT, sel_B TEXT, sel_C TEXT, sel_D TEXT,
            sel_E TEXT, sel_F TEXT, sel_G TEXT, sel_H TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_user_data(email):
    conn = sqlite3.connect(USER_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_electives WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row

def save_user_data(email, grade, class_nm, sel_dict):
    conn = sqlite3.connect(USER_DB_PATH)
    conn.execute('''
        INSERT OR REPLACE INTO user_electives
        (email, grade, class_nm, sel_A, sel_B, sel_C, sel_D, sel_E, sel_F, sel_G, sel_H)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        email, grade, class_nm,
        sel_dict.get('선택 A', ''), sel_dict.get('선택 B', ''), 
        sel_dict.get('선택 C', ''), sel_dict.get('선택 D', ''), 
        sel_dict.get('선택 E', ''), sel_dict.get('선택 F', ''), 
        sel_dict.get('선택 G', ''), sel_dict.get('선택 H', '')
    ))
    conn.commit()
    conn.close()

init_user_db()

# --- 사이드바 ---
with st.sidebar:
    st.title("사용자 인증")
    if not st.user.is_logged_in:
        st.button("구글 로그인", on_click=st.login)
    else:
        st.write(f"**{st.user.name}**님")
        st.write(f"({st.user.email})")
        st.button("로그아웃", on_click=st.logout)

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

# --- 중식 탭 ---
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

# --- 시간표 탭 ---
with tab3:
    st.title('시간표 생성기')
    
    # 테마 설정 (다크모드 온오프)
    is_dark = st.toggle("🌙 다크 모드", value=False)
    
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
    else:
        st.info("💡 로그인하면 학년, 반, 선택과목 정보를 저장해둘 수 있습니다.")

    grades_list = ["1", "2", "3"]
    classes_list = [str(i) for i in range(1, 10)]
    grade_idx = grades_list.index(default_grade) if default_grade in grades_list else 0
    class_idx = classes_list.index(default_class) if default_class in classes_list else 0

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
                dic[f'선택 {i}'] = st.text_input(f'선택 {i}', value=saved_sel[f'선택 {key}' if (key:=i) else i])
                elective.add(f'선택 {i}')
        
        raw = raw.tolist()
        for i in range(35):
            if raw[i] in elective:
                raw[i] = dic[raw[i]]

    if st.user.is_logged_in:
        if st.button("💾 내 학급/선택과목 정보 저장"):
            save_user_data(st.user.email, grade, class_nm, dic)
            st.success("내 정보가 성공적으로 저장되었습니다!")

    result = np.array(raw).reshape(-1,7).T

    def create_timetable_image(data_array, dark_mode=False):
        days = ['월', '화', '수', '목', '금']
        periods = [f'{i}교시' for i in range(1, 8)]
        df_tt = pd.DataFrame(data_array, columns=days, index=periods)

        # 색상 정의
        bg_color = '#262730' if dark_mode else '#ffffff'
        text_color = '#ffffff' if dark_mode else '#000000'
        header_color = '#3d3f4b' if dark_mode else '#f2f2f2'
        grid_color = '#555555' if dark_mode else '#cccccc'

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor(bg_color)
        ax.axis('off')

        fe = fm.FontEntry(fname='./경기천년체/경기천년바탕_Bold.ttf', name='경기')
        fm.fontManager.ttflist.insert(0,fe)
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

        # 셀 속성 적용
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor(grid_color)
            cell.get_text().set_color(text_color)
            if row == 0 or col == -1: # 헤더 영역
                cell.set_facecolor(header_color)
                cell.get_text().set_weight('bold')
            else: # 본문 영역
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

# --- 석식 탭 ---
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
    
    if not meals: st.error("석식 정보를 찾을 수 없습니다.")
    else:
        for item in meals: st.markdown(f"- {item}")
    st.markdown(allergyinfo)