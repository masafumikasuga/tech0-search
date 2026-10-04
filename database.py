import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/tech0_search.db")

def get_connection():
    """DB への接続を取得する（data/ フォルダが無ければ自動作成）"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """schema.sql を読み込んで DB を初期化する"""
    conn = get_connection()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def _keywords_to_text(keywords) -> str:
    """keywords（リスト or 文字列）を DB 保存用のカンマ区切り文字列にする"""
    if not keywords:
        return ""
    if isinstance(keywords, str):
        return keywords
    return ",".join(keywords)

def insert_page(page: dict) -> int:
    """ページ情報を DB に登録する（同じURLは上書き）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO pages
            (url, title, description, full_text, author, category, keywords, word_count, crawled_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        page["url"],
        page["title"],
        page.get("description", ""),
        page.get("full_text", ""),
        page.get("author", ""),
        page.get("category", ""),
        _keywords_to_text(page.get("keywords")),
        page.get("word_count", 0),
        page.get("crawled_at", datetime.now().isoformat()),
    ))
    page_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return page_id

def get_all_pages() -> list:
    """DB に登録されている全ページ情報を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages ORDER BY crawled_at DESC")
    rows = cursor.fetchall()
    conn.close()
    pages = []
    for row in rows:
        p = dict(row)
        p["keywords"] = [k.strip() for k in (p.get("keywords") or "").split(",") if k.strip()]
        pages.append(p)
    return pages

def migrate_from_json(json_path: str = "pages_w2.json") -> int:
    """JSON ファイルから DB にページ情報を移行する"""
    import json as json
    with open(json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)
    for p in pages:
        insert_page(p)
    return len(pages)

def log_search_query(query: str, result_count: int, user_id: str = None):
    """検索クエリのログを DB に記録する"""
    pass