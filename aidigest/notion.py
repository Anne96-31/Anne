"""Notion API：每天在母頁底下開一個子頁，並清掉超過保存天數的舊頁。

需要環境變數 NOTION_TOKEN 與 NOTION_AI_DIGEST_PAGE_ID。
母頁必須在 Notion 上「⋯ → Connections」連到該 integration，否則 API 回 404。
"""

from __future__ import annotations

import logging
import re
import time
from datetime import date, timedelta

import requests

from . import config

log = logging.getLogger(__name__)

API = "https://api.notion.com/v1"
MAX_TEXT = 1900          # 單一 rich_text 上限 2000 字，留緩衝
MAX_CHILDREN = 90        # 單次請求上限 100 個區塊

# 只清理「標題符合我們自己產生的格式」的頁面，避免誤刪母頁底下的其他筆記
TITLE_PREFIX = "AI & Data 每日摘要"
_ID_RE = re.compile(r"([0-9a-fA-F]{32})$")
_TITLE_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


class NotionError(RuntimeError):
    pass


def normalize_id(raw: str) -> str:
    """接受純 ID、含連字號 ID，或直接貼上的 Notion 網址。

    ID 永遠在網址最後一段的結尾，所以只取結尾的 32 位十六進位 ——
    否則標題裡的 a-f 字母（例如 "AI-Data-"）會被當成 ID 的一部分。
    """
    if not raw:
        return ""
    segment = raw.strip().split("?")[0].split("#")[0].rstrip("/").split("/")[-1]
    match = _ID_RE.search(segment.replace("-", ""))
    if not match:
        raise NotionError(f"無法從 {raw!r} 解析出 Notion ID")
    uid = match.group(1).lower()
    return f"{uid[0:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:32]}"


def digest_page_date(title: str) -> date | None:
    """標題符合我們的格式就回傳日期，否則 None（代表不是我們產的，不要動）。"""
    if not title.startswith(TITLE_PREFIX):
        return None
    m = _TITLE_DATE_RE.search(title)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


# ---------- rich_text / 區塊產生器 ----------

def rich_text(text: str, *, bold: bool = False, italic: bool = False,
              code: bool = False, color: str = "default", link: str | None = None) -> list[dict]:
    text = text or ""
    chunks = [text[i:i + MAX_TEXT] for i in range(0, len(text), MAX_TEXT)] or [""]
    out = []
    for chunk in chunks:
        item: dict = {
            "type": "text",
            "text": {"content": chunk},
            "annotations": {"bold": bold, "italic": italic, "code": code, "color": color},
        }
        if link:
            item["text"]["link"] = {"url": link}
        out.append(item)
    return out


def heading(text: str, level: int = 2) -> dict:
    key = f"heading_{min(max(level, 1), 3)}"
    return {"object": "block", "type": key, key: {"rich_text": rich_text(text), "is_toggleable": False}}


def paragraph(rich: list[dict] | str) -> dict:
    rich = rich_text(rich) if isinstance(rich, str) else rich
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich}}


def bullet(rich: list[dict] | str, children: list[dict] | None = None) -> dict:
    rich = rich_text(rich) if isinstance(rich, str) else rich
    body: dict = {"rich_text": rich}
    if children:
        body["children"] = children
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": body}


def numbered(rich: list[dict] | str) -> dict:
    rich = rich_text(rich) if isinstance(rich, str) else rich
    return {"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": rich}}


def callout(text: str, emoji: str = "💡", color: str = "blue_background") -> dict:
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": rich_text(text),
                        "icon": {"type": "emoji", "emoji": emoji}, "color": color}}


def divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


# ---------- HTTP ----------

class Notion:
    def __init__(self, token: str = "", version: str = config.NOTION_VERSION):
        token = token or config.NOTION_TOKEN
        if not token:
            raise NotionError("缺少 NOTION_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Notion-Version": version,
            "Content-Type": "application/json",
        })

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        last = ""
        for attempt in range(1, 4):
            try:
                resp = self.session.request(method, f"{API}{path}", json=payload,
                                            timeout=config.HTTP_TIMEOUT + 15)
            except requests.RequestException as exc:
                last = str(exc)
                if attempt < 3:
                    time.sleep(3 * attempt)
                    continue
                raise NotionError(f"Notion 連線失敗：{last}") from exc
            if resp.status_code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(3 * attempt)
                continue
            if not resp.ok:
                raise NotionError(f"Notion API {resp.status_code}：{resp.text[:400]}")
            return resp.json()
        raise NotionError(f"Notion 連線失敗：{last}")

    def whoami(self) -> str:
        data = self.request("GET", "/users/me")
        return data.get("name") or data.get("bot", {}).get("owner", {}).get("type", "unknown")

    def create_digest_page(self, parent_page_id: str, title: str, blocks: list[dict]) -> str:
        payload = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "icon": {"type": "emoji", "emoji": "🤖"},
            "properties": {"title": {"title": rich_text(title)}},
            "children": blocks[:MAX_CHILDREN],
        }
        page = self.request("POST", "/pages", payload)
        for start in range(MAX_CHILDREN, len(blocks), MAX_CHILDREN):
            chunk = blocks[start:start + MAX_CHILDREN]
            self.request("PATCH", f"/blocks/{page['id']}/children", {"children": chunk})
            log.info("已追加 %d 個區塊", len(chunk))
        return page.get("url", "")

    def list_child_pages(self, parent_page_id: str) -> list[tuple[str, str]]:
        """母頁底下所有子頁面的 (id, 標題)。"""
        pages, cursor = [], None
        while True:
            path = f"/blocks/{parent_page_id}/children?page_size=100"
            if cursor:
                path += f"&start_cursor={cursor}"
            data = self.request("GET", path)
            for block in data.get("results", []):
                if block.get("type") == "child_page":
                    pages.append((block["id"], block["child_page"].get("title", "")))
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
        return pages

    def trash_page(self, page_id: str) -> None:
        """送進 Notion 垃圾桶（30 天內可還原，不是永久刪除）。"""
        self.request("PATCH", f"/pages/{page_id}", {"archived": True})


# ---------- 對外 ----------

def publish(title: str, blocks: list[dict]) -> str:
    if not config.NOTION_PAGE_ID:
        raise NotionError("請設定 NOTION_AI_DIGEST_PAGE_ID")
    return Notion().create_digest_page(normalize_id(config.NOTION_PAGE_ID), title, blocks)


def prune_pages(days: int, today: date | None = None, dry_run: bool = False) -> list[str]:
    """把超過保存天數的每日摘要頁面移進垃圾桶，回傳被清掉的標題。"""
    if days <= 0 or not (config.NOTION_TOKEN and config.NOTION_PAGE_ID):
        log.info("未設定 Notion 或 days<=0，略過頁面清理。")
        return []

    notion = Notion()
    cutoff = (today or date.today()) - timedelta(days=days)
    checked, removed = 0, []

    for page_id, title in notion.list_child_pages(normalize_id(config.NOTION_PAGE_ID)):
        page_date = digest_page_date(title)
        if page_date is None:
            continue                      # 不是我們產生的頁面，完全不碰
        checked += 1
        if page_date >= cutoff:
            continue
        if not dry_run:
            notion.trash_page(page_id)
        removed.append(title)
        log.info("%s：%s", "[dry-run] 將清理" if dry_run else "已移進垃圾桶", title)

    log.info("Notion 清理：檢查 %d 頁，%s %d 頁（保留最近 %d 天，早於 %s）",
             checked, "將清理" if dry_run else "已清理", len(removed), days, cutoff)
    return removed
