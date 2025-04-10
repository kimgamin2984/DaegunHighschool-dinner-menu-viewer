import streamlit as st
import fitz
from datetime import datetime
import os
from pytz import timezone

month = datetime.now(timezone('Asia/Seoul')).month
day = datetime.now(timezone('Asia/Seoul')).day
date_str = f"{month:02}월 {day:02}일"
filename = "Dinner_Menu.pdf"

st.title("오늘의 석식 메뉴")
st.write(f"조회일: {date_str}")

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