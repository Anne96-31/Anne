"""每日必看新聞：台股盤勢、產業趨勢、國際財經（RSS 彙整）。"""
import logging
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

log = logging.getLogger(__name__)


def _gnews(query, lang="zh-TW"):
    if lang == "en":
        return f"https://news.google.com/rss/search?q={quote(query)}+when:1d&hl=en-US&gl=US&ceid=US:en"
    return f"https://news.google.com/rss/search?q={quote(query)}+when:1d&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"


SECTIONS = [
    ("🇹🇼 台股盤勢與法人動向", [
        _gnews("台股 收盤 外資"),
        _gnews("台股 三大法人 買賣超"),
        "https://tw.stock.yahoo.com/rss?category=tw-market",
    ]),
    ("🔬 產業趨勢：半導體 / AI / 電子供應鏈", [
        _gnews("台積電 OR 半導體 OR AI伺服器 OR CoWoS"),
        _gnews("輝達 供應鏈 台廠"),
        _gnews("記憶體 報價 OR 面板 報價 OR PCB"),
    ]),
    ("🏭 傳產・金融・航運・能源", [
        _gnews("航運 運價 OR 鋼鐵 OR 塑化 OR 金控 獲利"),
        _gnews("營收 創新高 月營收"),
    ]),
    ("🌐 國際財經：Fed・美股・匯率・地緣政治", [
        _gnews("聯準會 OR Fed 利率"),
        _gnews("美股 收盤 那斯達克"),
        _gnews("新台幣 匯率 OR 美中 關稅 OR 地緣政治"),
        _gnews("Federal Reserve OR Wall Street stocks OR semiconductor tariffs", lang="en"),
    ]),
]


def _entry_time(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
    return None


def load_news(per_section: int = 8, max_age_hours: int = 36):
    import feedparser

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    result = []
    seen = set()
    for title, feeds in SECTIONS:
        items = []
        for url in feeds:
            try:
                parsed = feedparser.parse(url, agent="Mozilla/5.0 (twdaily report bot)")
            except Exception as e:  # noqa: BLE001
                log.warning("feed %s failed: %s", url, e)
                continue
            for e in parsed.entries:
                headline = e.get("title", "").strip()
                key = headline.split(" - ")[0][:40]
                ts = _entry_time(e)
                if not headline or key in seen or (ts and ts < cutoff):
                    continue
                seen.add(key)
                source = e.get("source", {}).get("title", "") if isinstance(e.get("source"), dict) else ""
                items.append({"title": headline, "link": e.get("link", ""), "source": source, "time": ts})
        items.sort(key=lambda x: x["time"] or cutoff, reverse=True)
        result.append((title, items[:per_section]))
    return result
