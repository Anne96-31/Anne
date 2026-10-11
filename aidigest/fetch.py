"""抓取 RSS / Atom（用 feedparser，與 repo 既有相依一致）。"""

from __future__ import annotations

import calendar
import html
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import feedparser
import requests

from . import config

log = logging.getLogger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


@dataclass
class Article:
    title: str
    link: str
    published: datetime          # 一律 UTC
    summary: str
    source_key: str
    source_name: str
    category: str
    source_weight: float
    score: float = 0.0
    themes: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def age_hours(self) -> float:
        return (datetime.now(timezone.utc) - self.published).total_seconds() / 3600

    @property
    def local_date(self) -> str:
        return self.published.astimezone(config.TPE).strftime("%Y-%m-%d")

    @property
    def dedup_key(self) -> str:
        return self.link.split("?")[0].rstrip("/")


def clean_text(raw: str, limit: int = 900) -> str:
    """把 HTML 摘要壓成乾淨純文字。"""
    if not raw:
        return ""
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()[:limit]


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def entry_datetime(entry) -> datetime:
    """feedparser 的 *_parsed 是 UTC 的 struct_time；沒有日期的就當成現在。

    用 EPOCH + timedelta 而不是 datetime.fromtimestamp()：後者在 Windows 上
    遇到超出平台範圍的時間戳會丟 OSError [Errno 22]，而 feed 裡偶爾就會有
    這種壞日期（實際踩到過）。
    """
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = entry.get(key)
        if not parsed:
            continue
        try:
            return EPOCH + timedelta(seconds=calendar.timegm(parsed))
        except (OverflowError, ValueError, TypeError):
            continue
    return datetime.now(timezone.utc)


def entry_summary(entry) -> str:
    for key in ("summary", "description"):
        if entry.get(key):
            return clean_text(entry[key])
    content = entry.get("content") or []
    if content:
        return clean_text(content[0].get("value", ""))
    return ""


def fetch_source(source: dict) -> list[Article]:
    # 先用 requests 取內容再交給 feedparser 解析：feedparser 自己抓取時不會跟隨
    # 轉址（arXiv 會回 302），在 Windows 上某些網址還會拋 [Errno 22]。
    resp = requests.get(source["url"], headers=config.REQUEST_HEADERS,
                        timeout=config.HTTP_TIMEOUT, allow_redirects=True)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)
    if not feed.entries:
        log.warning("抓不到內容 %-24s status=%s %s",
                    source["name"], resp.status_code, getattr(feed, "bozo_exception", ""))
        return []

    articles = []
    for entry in feed.entries:
        title = clean_text(entry.get("title", ""), 300)
        link = (entry.get("link") or "").strip()
        if not title or not link:
            continue
        articles.append(Article(
            title=title,
            link=link,
            published=entry_datetime(entry),
            summary=entry_summary(entry),
            source_key=source["key"],
            source_name=source["name"],
            category=source["category"],
            source_weight=float(source.get("weight", 1.0)),
        ))
    log.info("抓到 %4d 篇  %s", len(articles), source["name"])
    return articles


def fetch_all(sources: list[dict], lookback_days: int) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    collected: list[Article] = []
    seen_links: set[str] = set()
    for source in sources:
        try:
            items = fetch_source(source)
        except Exception as exc:                      # 單一來源壞掉不該拖垮整天
            log.warning("抓取失敗 %-24s %s", source["name"], exc)
            continue
        for art in items:
            if art.published < cutoff or art.dedup_key in seen_links:
                continue
            seen_links.add(art.dedup_key)
            collected.append(art)
    collected.sort(key=lambda a: a.published, reverse=True)
    return collected
