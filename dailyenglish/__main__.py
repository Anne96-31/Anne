"""每日商務英文課程：產生當天的學習目標與教材，寫入 Notion 資料庫。

執行：python -m dailyenglish [--dry-run]
需要環境變數 ANTHROPIC_API_KEY、NOTION_TOKEN、NOTION_ENGLISH_DATABASE_ID。
--dry-run 只產生課程並輸出 Markdown，不寫入 Notion。
"""
import argparse
import logging
import os
import sys
from datetime import datetime

from twdaily.notion import MAX_CHILDREN, Notion, markdown_to_blocks, rich_text
from twdaily.report import TPE

from .lesson import generate, to_markdown
from .news import load_headlines

log = logging.getLogger("dailyenglish")

PROPERTIES = {
    "日期": {"date": {}},
    "Day": {"number": {"format": "number"}},
    "主題": {"select": {}},
    "詞彙": {"rich_text": {}},
    "文法重點": {"rich_text": {}},
    "完成": {"checkbox": {}},
}


def _plain(prop):
    return "".join(t.get("plain_text", "") for t in (prop or {}).get("rich_text", []))


def load_history(client: Notion, db_id: str, before: str):
    """讀取之前的課程頁面：回傳 (已學詞彙, 最近文法主題, 已上課天數)。"""
    body = {"filter": {"property": "日期", "date": {"before": before}},
            "sorts": [{"property": "日期", "direction": "descending"}], "page_size": 100}
    pages = []
    while True:
        res = client.call("POST", f"/databases/{db_id}/query", body)
        pages += res.get("results", [])
        if not res.get("has_more"):
            break
        body["start_cursor"] = res["next_cursor"]
    words = [w.strip() for p in pages for w in _plain(p["properties"].get("詞彙")).split(",") if w.strip()]
    grammar = [g for g in (_plain(p["properties"].get("文法重點")) for p in pages[:14]) if g]
    return words, grammar, len(pages)


def publish(client: Notion, db_id: str, lesson, md: str, day: int, today: str):
    title_prop = client.ensure_schema(db_id, PROPERTIES)
    client.archive_same_day(db_id, today)
    blocks = markdown_to_blocks(md)
    page = client.call("POST", "/pages", {
        "parent": {"database_id": db_id},
        "icon": {"type": "emoji", "emoji": "📘"},
        "properties": {
            title_prop: {"title": rich_text(f"Day {day}｜{today}｜{lesson.article_title}")},
            "日期": {"date": {"start": today}},
            "Day": {"number": day},
            "主題": {"select": {"name": lesson.theme.replace(",", " ")}},
            "詞彙": {"rich_text": rich_text(", ".join(v.word for v in lesson.vocabulary))},
            "文法重點": {"rich_text": rich_text(lesson.grammar_title)},
            "完成": {"checkbox": False},
        },
        "children": blocks[:MAX_CHILDREN],
    })
    for i in range(MAX_CHILDREN, len(blocks), MAX_CHILDREN):
        client.call("PATCH", f"/blocks/{page['id']}/children", {"children": blocks[i:i + MAX_CHILDREN]})
    log.info("已寫入 Notion：%s", page.get("url"))
    return page


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只輸出 Markdown，不寫入 Notion")
    args = ap.parse_args(argv)

    now = datetime.now(TPE)
    today = now.date().isoformat()
    token = os.environ.get("NOTION_TOKEN")
    db_id = (os.environ.get("NOTION_ENGLISH_DATABASE_ID") or "").replace("-", "").split("?")[0][-32:]
    if not args.dry_run and (not token or not db_id):
        log.error("未設定 NOTION_TOKEN / NOTION_ENGLISH_DATABASE_ID")
        return 1

    client = Notion(token) if token and db_id else None
    words, grammar, done = load_history(client, db_id, today) if client else ([], [], 0)
    day = done + 1
    log.info("Day %d：已學 %d 個詞彙", day, len(words))

    lesson = generate(now.date(), load_headlines(), words, grammar)
    md = to_markdown(lesson, day, now.date())
    if args.dry_run:
        print(md)
        return 0
    publish(client, db_id, lesson, md, day, today)
    return 0


if __name__ == "__main__":
    sys.exit(main())
