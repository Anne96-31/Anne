"""把每堂課的筆記同步成 Notion 母頁底下的子頁。

用法：
    python -m sparklearn                 # 同步全部課程
    python -m sparklearn --lesson 1 3    # 只同步第 1、3 課
    python -m sparklearn --dry-run       # 只轉換、不連 Notion

需要環境變數 NOTION_TOKEN 與 NOTION_SPARK_PAGE_ID（母頁網址或 ID）。
同名頁面已存在時會清空內容後重寫，頁面網址和順序不變。
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

from aidigest.notion import MAX_CHILDREN, Notion, NotionError, normalize_id, rich_text

from .markdown import parse

log = logging.getLogger("sparklearn")

NOTES_DIR = Path(__file__).resolve().parent / "notes"
TITLE_PREFIX = "Spark & Databricks｜"
ICON = "⚡"


def lesson_files(lessons: list[int] | None = None) -> list[Path]:
    """notes/ 底下依檔名排序；檔名開頭的數字就是課號。"""
    files = sorted(NOTES_DIR.glob("[0-9]*.md"))
    if lessons:
        wanted = set(lessons)
        files = [f for f in files if int(re.match(r"\d+", f.name).group()) in wanted]
    return files


def build_page(path: Path) -> tuple[str, list[dict]]:
    title, blocks = parse(path.read_text(encoding="utf-8"))
    return TITLE_PREFIX + (title or path.stem), blocks


def _child_blocks(notion: Notion, block_id: str) -> list[dict]:
    blocks, cursor = [], None
    while True:
        path = f"/blocks/{block_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = notion.request("GET", path)
        blocks += data.get("results", [])
        if not data.get("has_more"):
            return blocks
        cursor = data.get("next_cursor")


def _append(notion: Notion, page_id: str, blocks: list[dict]) -> None:
    for start in range(0, len(blocks), MAX_CHILDREN):
        notion.request("PATCH", f"/blocks/{page_id}/children",
                       {"children": blocks[start:start + MAX_CHILDREN]})


def upsert_page(notion: Notion, parent_id: str, title: str, blocks: list[dict]) -> str:
    existing = {b["child_page"]["title"]: b["id"]
                for b in _child_blocks(notion, parent_id) if b.get("type") == "child_page"}

    if title in existing:
        page_id = existing[title]
        for block in _child_blocks(notion, page_id):
            notion.request("DELETE", f"/blocks/{block['id']}")
        _append(notion, page_id, blocks)
        log.info("已更新：%s（%d 個區塊）", title, len(blocks))
        return notion.request("GET", f"/pages/{page_id}").get("url", "")

    page = notion.request("POST", "/pages", {
        "parent": {"type": "page_id", "page_id": parent_id},
        "icon": {"type": "emoji", "emoji": ICON},
        "properties": {"title": {"title": rich_text(title)}},
        "children": blocks[:MAX_CHILDREN],
    })
    _append(notion, page["id"], blocks[MAX_CHILDREN:])
    log.info("已新增：%s（%d 個區塊）", title, len(blocks))
    return page.get("url", "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="把 Spark & Databricks 課程筆記同步到 Notion")
    parser.add_argument("--lesson", type=int, nargs="*", help="只同步指定課號，例如 --lesson 1 3")
    parser.add_argument("--dry-run", action="store_true", help="只轉換，不寫入 Notion")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    files = lesson_files(args.lesson)
    if not files:
        log.error("找不到符合的課程筆記（%s）", NOTES_DIR)
        return 1

    pages = [build_page(f) for f in files]
    if args.dry_run:
        for title, blocks in pages:
            log.info("[dry-run] %s：%d 個區塊", title, len(blocks))
        return 0

    token = os.environ.get("NOTION_TOKEN", "").strip()
    parent = os.environ.get("NOTION_SPARK_PAGE_ID", "").strip()
    if not token or not parent:
        log.error("請設定 NOTION_TOKEN 與 NOTION_SPARK_PAGE_ID（學習筆記要放的 Notion 母頁）")
        return 1

    try:
        notion = Notion(token)
        parent_id = normalize_id(parent)
        for title, blocks in pages:
            url = upsert_page(notion, parent_id, title, blocks)
            print(f"- [{title}]({url})")
    except NotionError as exc:
        log.error("%s", exc)
        if "404" in str(exc):
            log.error("母頁可能還沒連到 integration：在 Notion 母頁右上角 ⋯ → Connections 加入。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
