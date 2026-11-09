"""抓取過去一天的 AI 新聞標題（英文國際新聞 + 繁中科技新聞），作為每日 AI 資訊的素材。"""
import logging
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

log = logging.getLogger(__name__)

# (查詢字串, 語系)；語系決定 Google News 的地區版本
QUERIES = [
    ("OpenAI OR Anthropic OR \"Google DeepMind\" OR \"Meta AI\" OR xAI", "en"),
    ("\"AI model\" launch OR release", "en"),
    ("artificial intelligence startup funding OR acquisition", "en"),
    ("Nvidia OR TSMC AI chips OR data center", "en"),
    ("AI regulation OR policy OR lawsuit", "en"),
    ("AI agents OR open-source model OR research breakthrough", "en"),
    ("人工智慧 OR 生成式AI OR AI模型", "zh"),
    ("AI 伺服器 OR AI 晶片 台灣", "zh"),
]

_LOCALE = {
    "en": "hl=en-US&gl=US&ceid=US:en",
    "zh": "hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
}


def _url(query, lang):
    return f"https://news.google.com/rss/search?q={quote(query)}+when:1d&{_LOCALE[lang]}"


def load_headlines(limit: int = 40, per_query: int = 8, max_age_hours: int = 36):
    import feedparser

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    seen, items = set(), []
    for q, lang in QUERIES:
        try:
            parsed = feedparser.parse(_url(q, lang), agent="Mozilla/5.0 (dailyai bot)")
        except Exception as e:  # noqa: BLE001
            log.warning("feed %s failed: %s", q, e)
            continue
        for e in parsed.entries[:per_query]:
            title = e.get("title", "").strip()
            t = e.get("published_parsed")
            ts = datetime.fromtimestamp(time.mktime(t), tz=timezone.utc) if t else None
            if not title or title in seen or (ts and ts < cutoff):
                continue
            seen.add(title)
            items.append({"title": title, "link": e.get("link", ""),
                          "source": (e.get("source") or {}).get("title", "")})
    log.info("取得 %d 則 AI 新聞標題", len(items))
    return items[:limit]
