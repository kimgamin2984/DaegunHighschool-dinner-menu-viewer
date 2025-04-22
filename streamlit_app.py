import streamlit as st
import fitz
from datetime import datetime
import os
import requests
from pytz import timezone
from dotenv import load_dotenv

today = datetime.now(timezone('Asia/Seoul'))
month = today.month
day = today.day
date_str = f"{month:02}월 {day:02}일"
filename = "Dinner_Menu.pdf"

st.write(f"조회일: {date_str}")

st.divider()

st.title("[오늘 점심 메뉴]")

load_dotenv()
API_KEY = os.getenv("NEIS_KEY")

ATPT_OFCDC_SC_CODE = 'D10'
SD_SCHUL_CODE = '7240082'
today_str = today.strftime("%Y%m%d")

url = 'https://open.neis.go.kr/hub/mealServiceDietInfo'
params = {
    'KEY': API_KEY,
    'Type': 'json',
    'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
    'SD_SCHUL_CODE': SD_SCHUL_CODE,
    'MLSV_YMD': today_str
}

response = requests.get(url, params=params)
data = response.json()

try:
    meals = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
    cleaned_meals = meals.replace('<br/>', '\n')
    for item in cleaned_meals.strip().split("\n"):
        st.write(item.strip())
except:
    st.error("오늘은 급식 정보가 없거나 오류가 발생했어요.")

st.divider()

st.title("[오늘 석식 메뉴]")
if not os.path.exists(filename):
    st.error(f"{month}월 석식 PDF 파일이 존재하지 않습니다.")
else:
    doc = fitz.open(filename)
    menu_found = False
    for page in doc:
        tables = page.find_tables()
        if not tables:
            continue
        for table in tables:
            data = table.extract()
            for row in data:
                for i, cell in enumerate(row):
                    if cell and date_str in cell:
                        for next_row in data[data.index(row)+1:]:
                            if len(next_row) > i and next_row[i]:
                                menu_items = next_row[i].strip().split("\n")
                                for item in menu_items:
                                    st.markdown(f"- {item.strip()}")
                                menu_found = True
                                break
                        break
                if menu_found:
                    break
            if menu_found:
                break
        if menu_found:
            break
    if not menu_found:
        st.warning(f"{date_str} 석식 메뉴를 찾을 수 없습니다.")

st.divider()

st.title("[오늘의 시간표]")

ATPT_OFCDC_SC_CODE = 'D10'
SD_SCHUL_CODE = '7240082'
selected_grade = st.selectbox("학년을 선택하세요", ["1", "2", "3"])
selected_class = st.selectbox("반을 선택하세요", [str(i) for i in range(1, 10)])
GRADE = selected_grade
CLASS_NM = selected_class

ALL_TI_YMD = today.strftime("%Y%m%d")

url = 'https://open.neis.go.kr/hub/hisTimetable'
params = {
    'KEY': API_KEY,
    'Type': 'json',
    'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
    'SD_SCHUL_CODE': SD_SCHUL_CODE,
    'GRADE': GRADE,
    'CLASS_NM': CLASS_NM,
    'ALL_TI_YMD': ALL_TI_YMD
}

res = requests.get(url, params=params)
data = res.json()

try:
    timetable = data['hisTimetable'][1]['row']
    for period in timetable:
        st.write(f"{period['PERIO']}교시: {period['ITRT_CNTNT']}")
except:
    st.error("시간표 정보를 불러올 수 없어요.")