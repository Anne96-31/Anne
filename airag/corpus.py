"""把 digests/*.md 解析成可檢索的 chunk。

切塊策略：一張「文章卡片」就是一個 chunk（語意完整、天然有標題/來源/日期等 metadata），
另外每天的「今日重點」briefing 也是一個 chunk，用來回答「某天/某段期間的趨勢」這類問題。
不用固定字數切塊：摘要本身已經是 LLM 整理過的短文，硬切只會把一則新聞拆散。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

DATE_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
TITLE_RE = re.compile(r"^#\s+.*?(\d{4}-\d{2}-\d{2})")
ARTICLE_RE = re.compile(r"^###\s+\[(?P<title>.+?)\]\((?P<url>[^)\s]+)\)\s*$")
META_RE = re.compile(
    r"^\*(?P<source>.+?)\s+·\s+(?P<date>\d{4}-\d{2}-\d{2})\s+·\s+相關度\s+(?P<score>[\d.]+)"
    r"\s+·\s+(?P<label>.+?)\*\s*$"
)
FIELD_RE = re.compile(r"^-\s+\*\*(?P<key>.+?)\*\*：(?P<value>.*)$")
TAG_RE = re.compile(r"`#([^`]+)`")

PRIORITY_BY_LABEL = {"必讀": "must_read", "快速瀏覽": "skim", "存參考": "reference"}
FIELD_KEYS = {"內容": "summary", "對你的意義": "why", "今天可以做": "action", "原文標題": "original_title"}


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    date: str                       # 摘要日期 YYYY-MM-DD
    kind: str                       # "article" | "briefing"
    title: str
    url: str = ""
    source: str = ""
    priority: str = ""              # must_read / skim / reference
    relevance: float = 0.0          # aidigest 排序時算出的相關度
    summary: str = ""
    why: str = ""
    action: str = ""
    original_title: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def text(self) -> str:
        """送進索引與 LLM context 的內容（不含 URL，避免網址字串干擾檢索）。"""
        parts = [self.title, self.original_title, self.summary, self.why, self.action,
                 " ".join(self.tags)]
        return "\n".join(p for p in parts if p)

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id, "date": self.date, "kind": self.kind,
            "title": self.title, "url": self.url, "source": self.source,
            "priority": self.priority, "relevance": self.relevance,
            "summary": self.summary, "why": self.why, "action": self.action,
            "original_title": self.original_title, "tags": list(self.tags),
        }


def _chunk_id(date: str, key: str) -> str:
    return f"{date}:{hashlib.sha1(key.encode('utf-8')).hexdigest()[:10]}"


def parse_digest(markdown: str, *, date: str | None = None) -> list[Chunk]:
    """解析一份每日摘要。格式由 aidigest.render.build_markdown 產生。"""
    lines = markdown.splitlines()
    if date is None:
        for line in lines[:3]:
            if m := TITLE_RE.match(line):
                date = m.group(1)
                break
    if date is None:
        raise ValueError("找不到摘要日期（標題行或檔名都沒有 YYYY-MM-DD）")

    chunks: list[Chunk] = []
    briefing = next((ln[2:].strip() for ln in lines if ln.startswith("> ") and "⚠️" not in ln), "")
    if briefing:
        chunks.append(Chunk(chunk_id=_chunk_id(date, "briefing"), date=date, kind="briefing",
                            title=f"{date} 今日重點", summary=briefing))

    current: dict | None = None

    def flush() -> None:
        if current:
            chunks.append(Chunk(
                chunk_id=_chunk_id(date, current["url"]), date=date, kind="article",
                title=current["title"], url=current["url"], source=current.get("source", ""),
                priority=current.get("priority", ""), relevance=current.get("relevance", 0.0),
                summary=current.get("summary", ""), why=current.get("why", ""),
                action=current.get("action", ""), original_title=current.get("original_title", ""),
                tags=tuple(current.get("tags", ())),
            ))

    for line in lines:
        if m := ARTICLE_RE.match(line):
            flush()
            current = {"title": m.group("title").strip(), "url": m.group("url")}
            continue
        if line.startswith("## ") or line.strip() == "---":
            flush()
            current = None
            continue
        if current is None:
            continue
        if m := META_RE.match(line):
            current["source"] = m.group("source").strip()
            current["relevance"] = float(m.group("score"))
            current["priority"] = PRIORITY_BY_LABEL.get(m.group("label").strip(), "")
        elif m := FIELD_RE.match(line):
            key = FIELD_KEYS.get(m.group("key").strip())
            if key:
                current[key] = m.group("value").strip()
        elif line.startswith("- ") and (tags := TAG_RE.findall(line)):
            current["tags"] = [t.strip() for t in tags]
    flush()
    return chunks


def digest_files(directory: Path) -> list[Path]:
    """只收 YYYY-MM-DD.md（latest.md 是重複內容，state.json 不是摘要）。"""
    return sorted(p for p in Path(directory).glob("*.md") if DATE_FILE_RE.match(p.name))


def load_corpus(directory: Path) -> list[Chunk]:
    """讀整個資料夾。同一個 URL 出現在多天時只保留最新一天的那張卡片。"""
    by_key: dict[str, Chunk] = {}
    for path in digest_files(directory):
        date = DATE_FILE_RE.match(path.name).group(1)
        for chunk in parse_digest(path.read_text(encoding="utf-8"), date=date):
            key = chunk.url or chunk.chunk_id
            prev = by_key.get(key)
            if prev is None or chunk.date >= prev.date:
                by_key[key] = chunk
    return sorted(by_key.values(), key=lambda c: (c.date, c.kind != "briefing", -c.relevance))
