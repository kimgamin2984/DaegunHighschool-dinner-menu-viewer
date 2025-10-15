import re
import fitz
import os
import sqlite3
import sys

def parse_pdf(filename):
    result = {}
    if not os.path.exists(filename):
        print("석식 파일을 찾을 수 없습니다.")
        return result
    try:
        doc = fitz.open(filename)
        for page in doc:
            tables = page.find_tables()
            if not tables:
                continue
            for table in tables:
                data = table.extract()
                for row_idx, row in enumerate(data):
                    for col_idx, cell in enumerate(row):
                        if not isinstance(cell, str) or not cell.strip():
                            continue
                        m = re.match(r"(\d{2})월\s*(\d{2})일", cell.strip())
                        if not m:
                            continue
                        month, day = m.groups()
                        date_key = f"{filename[-10:-4]}{day}"
                        next_row_idx = row_idx + 1
                        if next_row_idx < len(data):
                            next_row = data[next_row_idx]
                            if len(next_row) > col_idx:
                                content = next_row[col_idx]
                                if not isinstance(content, str) or not content.strip():
                                    continue
                                lines = content.strip().split("\n")
                                cleaned_items = []
                                for line in lines:
                                    parts = [p.strip() for p in line.split("/") if p.strip()]
                                    for part in parts:
                                        m2 = re.search(r"(\d+(?:\.\d+)*)$", part)
                                        if m2:
                                            nums = m2.group(1)
                                            name = part[: -len(nums)].strip()
                                            if name:
                                                cleaned_items.append(f"{name} ({nums})")
                                            else:
                                                if cleaned_items:
                                                    cleaned_items[-1] += f" ({nums})"
                                        else:
                                            if part:
                                                cleaned_items.append(part)
                                if cleaned_items:
                                    result[date_key] = cleaned_items
        return result
    except Exception as e:
        print("파싱 오류:", e)
        return result

def update_db(db_path, data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dinner (
            date TEXT PRIMARY KEY,
            menu TEXT
        )
    """)
    for date_key, menu_items in data.items():
        menu_text = "\n".join(menu_items)
        cur.execute("""
            INSERT OR REPLACE INTO dinner (date, menu)
            VALUES (?, ?)
        """, (date_key, menu_text))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python update_db.py menu/파일명.pdf")
        sys.exit(1)

    filename = sys.argv[1]
    parsed = parse_pdf(filename)
    if parsed:
        update_db("dinner.db", parsed)
        print("DB 업데이트 완료")
    else:
        print("추출된 데이터가 없습니다.")