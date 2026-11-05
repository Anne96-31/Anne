"""產生平日學習時程的 iPhone 行事曆訂閱檔（schedule/study.ics）。

時段與「每日學習日程」網頁一致。改時段時改 BLOCKS，再執行：
    python -m schedule.make_ics
"""

from __future__ import annotations

from pathlib import Path

PAGE = "https://claude.ai/artifact/Ce2nALJ4LdQh6MsCaWdJtT"
START_DATE = "20261105"  # 第一天；之後每個平日重複
OUT = Path(__file__).with_name("study.ics")

# (uid, 開始, 結束, 標題, 說明)；休息和午餐不放進行事曆，避免通知太多
BLOCKS = [
    ("stock1", "0800", "0820", "📈 台股日報", "看市場儀表板、三大法人和必看新聞"),
    ("eng1", "0820", "0900", "📘 商務英文", "Notion 今日課程：10 個詞彙、商業文章和理解問題"),
    ("c0", "0915", "1005", "🎓 Coursera ①", "打開日程看這個時段要上哪一堂"),
    ("c1", "1020", "1120", "🎓 Coursera ②", "打開日程看這個時段要上哪一堂"),
    ("ai0", "1120", "1200", "🤖 AI 摘要 ①", "今天學習計畫的第 1 項"),
    ("c2", "1330", "1430", "🎓 Coursera ③", "打開日程看這個時段要上哪一堂"),
    ("c3", "1445", "1545", "🎓 Coursera ④", "打開日程看這個時段要上哪一堂"),
    ("ai1", "1545", "1615", "🤖 AI 摘要 ②", "今天學習計畫的第 2 項"),
    ("eng2", "1615", "1645", "📘 英文寫作", "寫 100–150 字，貼到 Notion 的「我的短文」"),
    ("sync", "1645", "1700", "✅ 同步 TF2 進度頁", "把今天做完的課在 TF2 進度頁也勾起來"),
    ("stock2", "1800", "1820", "📈 盤後檢查清單", "做日報最後一段的盤後功課"),
    ("c4", "1830", "1930", "🎓 Coursera ⑤", "打開日程看這個時段要上哪一堂"),
    ("book", "1945", "2030", "📖 手冊複習", "《從 ETL 到 Attention》Part 10：把這週的 Lab 和概念對起來"),
    ("ai2", "2030", "2100", "🤖 AI 摘要 ③", "今天學習計畫的第 3 項"),
    ("eng3", "2100", "2130", "📘 英文複習", "複習今天的 10 個詞彙，把短文貼給 Claude 批改"),
    ("wrap", "2130", "2200", "📝 今日回顧", "寫本週 3 行筆記，看一眼明天的安排"),
]

VTIMEZONE = [
    "BEGIN:VTIMEZONE",
    "TZID:Asia/Taipei",
    "BEGIN:STANDARD",
    "DTSTART:19700101T000000",
    "TZOFFSETFROM:+0800",
    "TZOFFSETTO:+0800",
    "TZNAME:CST",
    "END:STANDARD",
    "END:VTIMEZONE",
]


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line: str) -> list[str]:
    """RFC 5545：每行最多 75 bytes，續行以一個空白開頭；不切斷 UTF-8 字元。"""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        limit = 75 if not out else 74
        if size + n > limit:
            out.append(cur)
            cur, size = "", 0
        cur += ch
        size += n
    out.append(cur)
    return [out[0]] + [" " + s for s in out[1:]]


def build() -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//anne96-31//daily-study//ZH",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:每日學習日程",
        "X-WR-TIMEZONE:Asia/Taipei",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
        *VTIMEZONE,
    ]
    for uid, start, end, title, desc in BLOCKS:
        lines += [
            "BEGIN:VEVENT",
            f"UID:daily-study-{uid}@anne96-31",
            "DTSTAMP:20261105T000000Z",
            f"DTSTART;TZID=Asia/Taipei:{START_DATE}T{start}00",
            f"DTEND;TZID=Asia/Taipei:{START_DATE}T{end}00",
            "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
            f"SUMMARY:{escape(title)}",
            f"DESCRIPTION:{escape(desc + chr(10) + '打勾：' + PAGE)}",
            f"URL:{PAGE}",
            "TRANSP:TRANSPARENT",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{escape(title)}",
            "TRIGGER:PT0M",
            "END:VALARM",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "".join(f + "\r\n" for line in lines for f in fold(line))


def main() -> None:
    OUT.write_bytes(build().encode("utf-8"))
    print(f"wrote {OUT} ({len(BLOCKS)} events)")


if __name__ == "__main__":
    main()
