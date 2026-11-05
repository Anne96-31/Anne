"""抓取過去一天的英文商業新聞標題，作為每日閱讀文章的素材。"""
import logging
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

log = logging.getLogger(__name__)

QUERIES = [
    "business news", "global economy", "earnings OR merger OR acquisition",
    "semiconductor OR artificial intelligence industry", "Federal Reserve OR central bank",
]


def _url(query):
    return f"https://news.google.com/rss/search?q={quote(query)}+when:1d&hl=en-US&gl=US&ceid=US:en"


def load_headlines(limit: int = 15, max_age_hours: int = 36):
    import feedparser

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    seen, items = set(), []
    for q in QUERIES:
        try:
            parsed = feedparser.parse(_url(q), agent="Mozilla/5.0 (dailyenglish bot)")
        except Exception as e:  # noqa: BLE001
            log.warning("feed %s failed: %s", q, e)
            continue
        for e in parsed.entries[:6]:
            title = e.get("title", "").strip()
            t = e.get("published_parsed")
            ts = datetime.fromtimestamp(time.mktime(t), tz=timezone.utc) if t else None
            if not title or title in seen or (ts and ts < cutoff):
                continue
            seen.add(title)
            items.append({"title": title, "link": e.get("link", "")})
    log.info("取得 %d 則英文商業新聞標題", len(items))
    return items[:limit]
