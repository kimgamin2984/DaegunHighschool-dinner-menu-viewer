import sqlite3
import streamlit as st
from datetime import datetime
import os
import requests
from pytz import timezone
from dotenv import load_dotenv
import db_update
import streamlit as st
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
        sel_dict.get('선택A', ''), sel_dict.get('선택B', ''), 
        sel_dict.get('선택C', ''), sel_dict.get('선택D', ''), 
        sel_dict.get('선택E', ''), sel_dict.get('선택F', ''), 
        sel_dict.get('선택G', ''), sel_dict.get('선택H', '')
    ))
    conn.commit()
    conn.close()

# 앱 실행 시 DB 테이블이 없으면 생성
init_user_db()

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
month = today.month
day = today.day
date_str = f"{month:02}월 {day:02}일"
today_str = today.strftime("%Y%m%d")

filename = os.path.join("menu", f"{today.year}{today.month:02}.pdf")
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
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
        'SD_SCHUL_CODE': SD_SCHUL_CODE,
        'MLSV_YMD': today_str
    }
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

# with tab3:
#     st.markdown("## 시간표")

#     grade = st.selectbox("학년", ["1", "2", "3"], index=0)
#     class_nm = st.selectbox("반", [str(i) for i in range(1, 10)], index=0)

#     url = 'https://open.neis.go.kr/hub/hisTimetable'
#     params = {
#         'KEY': API_KEY,
#         'Type': 'json',
#         'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
#         'SD_SCHUL_CODE': SD_SCHUL_CODE,
#         'GRADE': grade,
#         'CLASS_NM': class_nm,
#         'ALL_TI_YMD': today_str
#     }

#     try:
#         res = requests.get(url, params=params, stream=True)
#         raw = res.raw.read(decode_content=True)
#         data = json.loads(raw)
#         timetable = data['hisTimetable'][1]['row']
#         for period in timetable:
#             st.text(f"{period['PERIO']}교시: {period['ITRT_CNTNT']}")
#     except:
#         st.error("시간표 정보를 불러올 수 없습니다.")

# with tab3:

#     st.title('시간표 생성기')

#     elective = set()
#     grade = st.selectbox("학년", ["1", "2", "3"], index=0)
#     class_nm = st.selectbox("반", [str(i) for i in range(1, 10)], index=0)
#     code1 = float(f'{grade}0{class_nm}1')

#     df = pd.read_excel('Timetable_all_raw.xlsx', header=None)
#     print(df)
#     raw = df.loc[df[0] == code1, 2:36].iloc[0]
#     if grade != '1':
#         dic = {}
#         for i in 'ABCDEFGH':
#             dic[f'선택{i}'] = st.text_input(f'선택{i}')
#             elective.add(f'선택{i}')
#         raw = raw.tolist()
#         for i in range(35):
#             if raw[i] in elective:
#                 raw[i] = dic[raw[i]]
#     result = np.array(raw).reshape(-1,7).T

#     def create_timetable_image(data_array):
#         # 1. 요일과 교시 라벨 준비
#         days = ['월', '화', '수', '목', '금']
#         periods = [f'{i}교시' for i in range(1, 8)]

#         # 2. 6x8 데이터프레임 재구성 (요일 행 + 교시 열 추가)
#         # result가 (5, 7)이므로 전치(T) 상태라면 행이 요일, 열이 교시일 수 있음
#         # 만약 result가 (7, 5)라면 그대로 쓰면 됨. 여기서는 result를 (7, 5)로 가정 (7행 5열)
#         df_tt = pd.DataFrame(data_array, columns=days, index=periods)

#         # 3. 시각화 설정
#         fig, ax = plt.subplots(figsize=(10, 8))
#         ax.axis('off')

#         # 한글 폰트 설정 (필수!)
#         fe = fm.FontEntry(fname='./경기천년체/경기천년바탕_Bold.ttf', name='경기')
#         fm.fontManager.ttflist.insert(0,fe)
#         plt.rc('font', family='경기')
#         plt.rcParams['axes.unicode_minus'] = False 

#         # 4. 표 그리기 (header와 index 포함)
#         # cellText에는 데이터, colLabels에는 요일, rowLabels에는 교시
#         table = ax.table(
#             cellText=df_tt.values,
#             colLabels=df_tt.columns,
#             rowLabels=df_tt.index,
#             cellLoc='center',
#             loc='center',
#             colColours=['#f2f2f2'] * 5,  # 요일 칸 색상
#             rowColours=['#f2f2f2'] * 7   # 교시 칸 색상
#         )

#         # 5. 스타일링: 시간표답게 큼직하게
#         table.auto_set_font_size(True)
#         table.scale(1, 4)

#         # 6. 버퍼 저장
#         buf = BytesIO()
#         plt.savefig(buf, format="png", bbox_inches='tight', dpi=300)
#         buf.seek(0)
#         plt.close(fig)
#         return buf

#     st.markdown('---')

#     # --- 실행부 ---
#     # 현재 가진 result가 (7, 5) 사이즈라고 가정합니다. (7행:교시, 5열:요일)
#     # 만약 (5, 7)이라면 result.T를 넣으세요.
#     try:
#         img_buf = create_timetable_image(result)
        
#         st.write("### 🕒 완성된 시간표")
#         st.image(img_buf) # 화면에 미리보기 출력

#         st.download_button(
#             label="💾 시간표 이미지 다운로드",
#             data=img_buf,
#             file_name="timetable.png",
#             mime="image/png"
#         )
#     except Exception as e:
#         st.error(f"시간표 생성 실패: {e}")

with tab3:
    st.title('시간표 생성기')

    # [추가] 초기값 설정용 변수
    default_grade = "1"
    default_class = "1"
    saved_sel = {f'선택{i}': '' for i in 'ABCDEFGH'}

    # [추가] 로그인 되어있다면 기존 DB에서 데이터 불러오기
    if st.user.is_logged_in:
        user_row = load_user_data(st.user.email)
        if user_row:
            # user_row 순서: 0:email, 1:grade, 2:class, 3~10:선택A~H
            default_grade = user_row[1]
            default_class = user_row[2]
            for idx, key in enumerate('ABCDEFGH'):
                saved_sel[f'선택{key}'] = user_row[3 + idx]
    else:
        st.info("💡 로그인하면 학년, 반, 선택과목 정보를 저장해둘 수 있습니다.")

    elective = set()
    
    # [수정] selectbox의 index를 DB에서 불러온 값으로 설정
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
        df = pd.read_excel('Timetable_all_raw.xlsx', header=None)
        raw = df.loc[df[0] == code1, 2:36].iloc[0]
    except Exception as e:
        st.error("엑셀 파일에서 해당 반의 시간표 데이터를 찾을 수 없습니다.")
        st.stop()

    dic = {}
    if grade != '1':
        st.markdown("#### 선택과목 입력")
        # 4개씩 2줄로 입력칸 배치 (레이아웃 최적화)
        cols1 = st.columns(4)
        cols2 = st.columns(4)
        all_cols = cols1 + cols2
        
        for idx, i in enumerate('ABCDEFGH'):
            with all_cols[idx]:
                # [수정] text_input의 기본값을 DB에서 불러온 값으로 설정
                dic[f'선택{i}'] = st.text_input(f'선택{i}', value=saved_sel[f'선택{i}'])
                elective.add(f'선택{i}')
        
        raw = raw.tolist()
        for i in range(35):
            if raw[i] in elective:
                raw[i] = dic[raw[i]]

    # [추가] 내 정보 저장하기 버튼 (로그인 된 경우만 보임)
    if st.user.is_logged_in:
        if st.button("💾 내 학급/선택과목 정보 저장"):
            save_user_data(st.user.email, grade, class_nm, dic)
            st.success("내 정보가 성공적으로 저장되었습니다! 다음번 접속 시 자동으로 불러옵니다.")

    result = np.array(raw).reshape(-1,7).T

    def create_timetable_image(data_array):
        days = ['월', '화', '수', '목', '금']
        periods = [f'{i}교시' for i in range(1, 8)]

        df_tt = pd.DataFrame(data_array, columns=days, index=periods)

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.axis('off')

        fe = fm.FontEntry(fname='./경기천년체/경기천년바탕_Bold.ttf', name='경기')
        fm.fontManager.ttflist.insert(0,fe)
        plt.rc('font', family='경기')
        plt.rcParams['axes.unicode_minus'] = False 

        table = ax.table(
            cellText=df_tt.values,
            colLabels=df_tt.columns,
            rowLabels=df_tt.index,
            cellLoc='center',
            loc='center',
            colColours=['#f2f2f2'] * 5,  
            rowColours=['#f2f2f2'] * 7   
        )

        table.auto_set_font_size(True)
        table.scale(1, 4)

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', dpi=300)
        buf.seek(0)
        plt.close(fig)
        return buf

    st.markdown('---')

    try:
        img_buf = create_timetable_image(result)
        
        st.write("### 🕒 완성된 시간표")
        st.image(img_buf) 

        st.download_button(
            label="다운로드",
            data=img_buf,
            file_name="timetable.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"시간표 생성 실패: {e}")

with tab2:
    st.markdown("## 석식 식단")

    DB_PATH = "dinner_menu.db"

    msg = st.empty()

    def load_from_db(date):
        import sqlite3
        if not os.path.exists(DB_PATH):
            return None
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT menu FROM dinner WHERE date = ?", (date,))
            row = cur.fetchone()
            conn.close()
            if row:
                return row[0].split("\n")
        except:
            pass
        return None

    meals = load_from_db(today_str)

    if not meals:
        msg.info("API 호출 중...")

        try:
            ok = db_update.update_db(DB_PATH, today_str, DINNER_KEY)

            if ok:
                meals = load_from_db(today_str)
                msg.empty()
            else:
                msg.empty()
        except Exception as e:
            msg.empty()
            st.error("DB 업데이트 중 오류 발생")
            st.error(e)

    else:
        msg.empty()

    if not meals:
        st.error("석식 정보를 찾을 수 없습니다.")
    else:
        for item in meals:
            st.markdown(f"- {item}")

    st.markdown(allergyinfo)