import sqlite3
import requests


API_URL = "https://daegundinnerapi.onrender.com/menu"


def fetch_menu(date: str, api_key: str):
    params = {
        "date": date,
        "key": api_key
    }

    try:
        res = requests.get(API_URL, params=params)
        data = res.json()

        if "menu" in data:
            return data["menu"]
        else:
            return None

    except Exception as e:
        print("API 요청 오류:", e)
        return None


def update_db(db_path: str, date: str, api_key: str):

    menu_items = fetch_menu(date, api_key)
    if menu_items is None:
        print(f"API로부터 메뉴 불러오기 실패 ({date})")
        return False

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dinner (
            date TEXT PRIMARY KEY,
            menu TEXT
        )
    """)

    menu_text = "\n".join(menu_items)

    cur.execute("""
        INSERT OR REPLACE INTO dinner (date, menu)
        VALUES (?, ?)
    """, (date, menu_text))

    conn.commit()
    conn.close()
    print(f"DB 업데이트 완료: {date}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("사용법: python db_update.py YYYYMMDD API_KEY")
        sys.exit(1)

    date = sys.argv[1]
    api_key = sys.argv[2]

    if not (len(date) == 8 and date.isdigit()):
        print("잘못된 날짜 형식입니다. 예: 20250304")
        sys.exit(1)

    update_db("dinner_menu.db", date, api_key)