import json
import streamlit as st
from datetime import datetime
import os
import requests
from pytz import timezone
from dotenv import load_dotenv
import db_update
from streamlit_google_auth import Authenticate

auth = Authenticate(
    json_path='client_secret.json', 
    cookie_name='daegun_auth',
    cookie_key='your_secret_key',
    cookie_expiry_days=30,
)

# 만약 위에서 에러나면 secret_path를 json_path로만 바꿔봐. 
# 최신 버전은 json_path를 써야 함.

auth.check_authenticator()

with st.sidebar:
    if st.session_state.get('connected'):
        st.write(f"{st.session_state['name']}님")
        auth.logout("로그아웃", location='sidebar')
    else:
        auth.login("구글 로그인", location='sidebar')

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

with tab3:
    st.markdown("## 시간표")

    grade = st.selectbox("학년", ["1", "2", "3"], index=0)
    class_nm = st.selectbox("반", [str(i) for i in range(1, 10)], index=0)

    url = 'https://open.neis.go.kr/hub/hisTimetable'
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
        'SD_SCHUL_CODE': SD_SCHUL_CODE,
        'GRADE': grade,
        'CLASS_NM': class_nm,
        'ALL_TI_YMD': today_str
    }

    try:
        res = requests.get(url, params=params, stream=True)
        raw = res.raw.read(decode_content=True)
        data = json.loads(raw)
        timetable = data['hisTimetable'][1]['row']
        for period in timetable:
            st.text(f"{period['PERIO']}교시: {period['ITRT_CNTNT']}")
    except:
        st.error("시간표 정보를 불러올 수 없습니다.")

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