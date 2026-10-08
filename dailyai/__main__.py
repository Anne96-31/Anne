"""每日 AI 資訊：整理過去一天的 AI 新聞，寫入 Notion 資料庫。

執行：python -m dailyai [--dry-run]
需要環境變數 ANTHROPIC_API_KEY、NOTION_TOKEN、NOTION_AI_DATABASE_ID。
--dry-run 只產生快報並輸出 Markdown，不寫入 Notion。
"""
import argparse
import logging
import os
import sys
from datetime import datetime

from twdaily.notion import MAX_CHILDREN, Notion, markdown_to_blocks, rich_text
from twdaily.report import TPE

from .brief import generate, to_markdown
from .news import load_headlines

log = logging.getLogger("dailyai")

PROPERTIES = {
    "日期": {"date": {}},
    "重點": {"rich_text": {}},
    "標籤": {"multi_select": {}},
    "則數": {"number": {"format": "number"}},
    "新聞標題": {"rich_text": {}},
    "術語": {"rich_text": {}},
    "已讀": {"checkbox": {}},
}

SEP = "；"


def _plain(prop):
    return "".join(t.get("plain_text", "") for t in (prop or {}).get("rich_text", []))


def load_history(client: Notion, db_id: str, before: str):
    """讀取最近的快報：回傳 (近 3 天已報導的新聞標題, 近 30 天的術語)。"""
    res = client.call("POST", f"/databases/{db_id}/query", {
        "filter": {"property": "日期", "date": {"before": before}},
        "sorts": [{"property": "日期", "direction": "descending"}], "page_size": 30})
    pages = res.get("results", [])
    titles = [t for p in pages[:3] for t in _plain(p["properties"].get("新聞標題")).split(SEP) if t]
    terms = [t for t in (_plain(p["properties"].get("術語")) for p in pages) if t]
    return titles, terms


def publish(client: Notion, db_id: str, brief, md: str, today: str):
    title_prop = client.ensure_schema(db_id, PROPERTIES)
    client.archive_same_day(db_id, today)
    blocks = markdown_to_blocks(md)
    page = client.call("POST", "/pages", {
        "parent": {"database_id": db_id},
        "icon": {"type": "emoji", "emoji": "🤖"},
        "properties": {
            title_prop: {"title": rich_text(f"{today}｜{brief.headline_zh}")},
            "日期": {"date": {"start": today}},
            "重點": {"rich_text": rich_text("\n".join(brief.takeaways_zh))},
            "標籤": {"multi_select": [{"name": t.replace(",", " ")[:100]} for t in brief.tags]},
            "則數": {"number": len(brief.items)},
            "新聞標題": {"rich_text": rich_text(SEP.join(i.title_zh for i in brief.items))},
            "術語": {"rich_text": rich_text(brief.term.term)},
            "已讀": {"checkbox": False},
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
    db_id = (os.environ.get("NOTION_AI_DATABASE_ID") or "").replace("-", "").split("?")[0][-32:]
    if not args.dry_run and (not token or not db_id):
        log.error("未設定 NOTION_TOKEN / NOTION_AI_DATABASE_ID")
        return 1

    headlines = load_headlines()
    if not headlines:
        log.error("抓不到任何 AI 新聞，今天不產生快報")
        return 1

    client = Notion(token) if token and db_id else None
    covered, terms = load_history(client, db_id, today) if client else ([], [])
    brief = generate(now.date(), headlines, covered, terms)
    md = to_markdown(brief, now.date())
    if args.dry_run:
        print(md)
        return 0
    publish(client, db_id, brief, md, today)
    return 0


if __name__ == "__main__":
    sys.exit(main())
