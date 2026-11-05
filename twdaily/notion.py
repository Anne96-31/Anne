"""把每日日報同步到 Notion 資料庫：每天一頁，重點數字放在資料庫欄位方便篩選排序。

執行：python -m twdaily.notion reports/latest.md reports/latest.json
需要環境變數 NOTION_TOKEN（Integration 金鑰）與 NOTION_DATABASE_ID。
"""
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import requests

from .cleanup import DEFAULT_DAYS, cutoff_date

log = logging.getLogger(__name__)

API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
MAX_TEXT = 2000      # 單一 rich_text 的字數上限
MAX_CHILDREN = 100   # 單次請求的區塊數上限

PROPERTIES = {
    "日期": {"date": {}},
    "入選檔數": {"number": {"format": "number"}},
    "加權指數": {"number": {"format": "number_with_commas"}},
    "加權漲跌%": {"number": {"format": "number"}},
    "外資買賣超(億)": {"number": {"format": "number"}},
    "前五名": {"rich_text": {}},
    "集中產業": {"multi_select": {}},
    "報告連結": {"url": {}},
}

# ---------- Markdown -> Notion 區塊 ----------

_INLINE = re.compile(r"\*\*(?P<bold>.+?)\*\*|\[(?P<text>[^\]]+)\]\((?P<url>[^)]+)\)|`(?P<code>[^`]+)`")


def rich_text(s: str):
    """支援 **粗體**、[連結](url)、`程式碼`；整行 _斜體_ 也會處理。"""
    italic = len(s) > 2 and s.startswith("_") and s.endswith("_")
    if italic:
        s = s[1:-1]
    parts, pos = [], 0
    for m in _INLINE.finditer(s):
        if m.start() > pos:
            parts.append((s[pos:m.start()], {}, None))
        if m.group("bold") is not None:
            parts.append((m.group("bold"), {"bold": True}, None))
        elif m.group("text") is not None:
            url = m.group("url")
            parts.append((m.group("text"), {}, url if url.startswith("http") else None))
        else:
            parts.append((m.group("code"), {"code": True}, None))
        pos = m.end()
    if pos < len(s):
        parts.append((s[pos:], {}, None))

    out = []
    for text, ann, url in parts:
        if italic:
            ann = {**ann, "italic": True}
        for i in range(0, len(text), MAX_TEXT):
            item = {"type": "text", "text": {"content": text[i:i + MAX_TEXT]}}
            if url:
                item["text"]["link"] = {"url": url}
            if ann:
                item["annotations"] = ann
            out.append(item)
    return out


def _block(kind, text, **extra):
    return {"object": "block", "type": kind, kind: {"rich_text": rich_text(text), **extra}}


def _table(lines):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]
    width = max(len(r) for r in rows)
    children = [{"object": "block", "type": "table_row",
                 "table_row": {"cells": [rich_text(c) for c in r + [""] * (width - len(r))]}}
                for r in rows]
    return {"object": "block", "type": "table",
            "table": {"table_width": width, "has_column_header": True, "has_row_header": False,
                      "children": children}}


def markdown_to_blocks(md: str):
    blocks, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            blocks.append(_table(lines[i:j]))
            i = j
            continue
        i += 1
        if not line.strip():
            continue
        if m := re.match(r"(#{1,3}) (.*)", line):
            blocks.append(_block(f"heading_{len(m.group(1))}", m.group(2)))
        elif line.startswith("> "):
            blocks.append(_block("quote", line[2:]))
        elif m := re.match(r"- \[( |x)\] (.*)", line):
            blocks.append(_block("to_do", m.group(2), checked=m.group(1) == "x"))
        elif line.startswith("- "):
            blocks.append(_block("bulleted_list_item", line[2:]))
        elif m := re.match(r"\d+\. (.*)", line):
            blocks.append(_block("numbered_list_item", m.group(1)))
        else:
            blocks.append(_block("paragraph", line))
    return blocks


# ---------- Notion API ----------

class Notion:
    def __init__(self, token: str):
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION,
                               "Content-Type": "application/json"})

    def call(self, method, path, body=None):
        for attempt in range(4):
            r = self.s.request(method, f"{API}{path}", json=body, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(float(r.headers.get("Retry-After", 2 ** attempt)))
                continue
            if not r.ok:
                raise RuntimeError(f"Notion API {method} {path} -> {r.status_code}: {r.text}")
            return r.json()
        raise RuntimeError(f"Notion API {method} {path} 重試後仍失敗")

    def ensure_schema(self, db_id, properties=PROPERTIES):
        """補上缺少的欄位，回傳標題欄位名稱。"""
        db = self.call("GET", f"/databases/{db_id}")
        props = db["properties"]
        missing = {k: v for k, v in properties.items() if k not in props}
        if missing:
            log.info("新增 Notion 欄位：%s", "、".join(missing))
            self.call("PATCH", f"/databases/{db_id}", {"properties": missing})
        return next(k for k, v in props.items() if v["type"] == "title")

    def archive_same_day(self, db_id, date):
        """重新執行同一天時，先封存舊頁面避免重複。"""
        res = self.call("POST", f"/databases/{db_id}/query",
                        {"filter": {"property": "日期", "date": {"equals": date}}})
        for page in res.get("results", []):
            self.call("PATCH", f"/pages/{page['id']}", {"archived": True})

    def prune_before(self, db_id, cutoff: str):
        """封存（移到垃圾桶）日期早於 cutoff 的日報頁面，回傳封存數量。"""
        body = {"filter": {"property": "日期", "date": {"before": cutoff}}, "page_size": 100}
        archived = 0
        while True:
            res = self.call("POST", f"/databases/{db_id}/query", body)
            for page in res.get("results", []):
                self.call("PATCH", f"/pages/{page['id']}", {"archived": True})
                archived += 1
            if not res.get("has_more"):
                return archived
            body["start_cursor"] = res["next_cursor"]


def page_properties(summary, title_prop, report_url=None):
    def num(v):
        return {"number": v}

    props = {
        title_prop: {"title": rich_text(f"{summary['report_date']} 台股日報｜入選 {summary['picks']} 檔")},
        "日期": {"date": {"start": summary["report_date"]}},
        "入選檔數": num(summary["picks"]),
        "加權指數": num(summary.get("twii")),
        "加權漲跌%": num(summary.get("twii_d1")),
        "外資買賣超(億)": num(summary.get("foreign_net")),
        "前五名": {"rich_text": rich_text("、".join(summary.get("top_picks") or []) or "—")},
        "集中產業": {"multi_select": [{"name": n.replace(",", " ")} for n in summary.get("industries") or []]},
    }
    if report_url:
        props["報告連結"] = {"url": report_url}
    return props


def publish(md_path: Path, summary_path: Path, token: str, db_id: str, report_url=None):
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    blocks = markdown_to_blocks(md_path.read_text(encoding="utf-8"))
    client = Notion(token)
    title_prop = client.ensure_schema(db_id)
    client.archive_same_day(db_id, summary["report_date"])
    page = client.call("POST", "/pages", {
        "parent": {"database_id": db_id},
        "icon": {"type": "emoji", "emoji": "📈"},
        "properties": page_properties(summary, title_prop, report_url),
        "children": blocks[:MAX_CHILDREN],
    })
    for i in range(MAX_CHILDREN, len(blocks), MAX_CHILDREN):
        client.call("PATCH", f"/blocks/{page['id']}/children", {"children": blocks[i:i + MAX_CHILDREN]})
    log.info("已發布到 Notion：%s", page.get("url"))
    return page


def _report_url(date):
    server, repo = os.environ.get("GITHUB_SERVER_URL"), os.environ.get("GITHUB_REPOSITORY")
    branch = os.environ.get("GITHUB_REF_NAME", "master")
    return f"{server}/{repo}/blob/{branch}/reports/{date}.md" if server and repo else None


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    token, db_id = os.environ.get("NOTION_TOKEN"), os.environ.get("NOTION_DATABASE_ID")
    if not token or not db_id:
        log.warning("未設定 NOTION_TOKEN / NOTION_DATABASE_ID，略過 Notion 同步")
        return
    md = Path(sys.argv[1] if len(sys.argv) > 1 else "reports/latest.md")
    summary = Path(sys.argv[2] if len(sys.argv) > 2 else "reports/latest.json")
    date = json.loads(summary.read_text(encoding="utf-8"))["report_date"]
    db_id = db_id.replace("-", "").split("?")[0][-32:]
    publish(md, summary, token, db_id, _report_url(date))

    days = int(os.environ.get("RETENTION_DAYS", DEFAULT_DAYS))
    cutoff = cutoff_date(days).isoformat()
    n = Notion(token).prune_before(db_id, cutoff)
    log.info("Notion：封存 %d 頁超過 %d 天的日報（早於 %s）", n, days, cutoff)


if __name__ == "__main__":
    main()
