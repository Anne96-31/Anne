"""產生 Markdown 日報。"""
from datetime import timedelta, timezone

TPE = timezone(timedelta(hours=8))

GUIDE = """\
### 📘 如何解讀這份清單（新手必讀）

| 欄位 | 意義 | 怎麼看 |
|---|---|---|
| 訊號 | **低檔金叉**：DIF 在零軸下方上穿 DEM，柱狀體 OSC 由綠翻紅；**DIF翻正**：DIF 由負轉正站上零軸 | 兩者同時出現（低檔金叉+DIF翻正）通常較強 |
| 評分 | 0–7 分：訊號數×2 + 站上月線 + 爆量(量比≥1.5) + RSI 40–65 未過熱 + OSC 連續放大 | 分數高代表「確認條件」多，不代表一定會漲 |
| 區間位置 | 收盤價在近 120 日高低區間的位置，0% = 最低、100% = 最高 | 越低越接近「低檔」，但也可能是弱勢股 |
| 量比 | 今日成交量 ÷ 前 20 日均量 | ≥1.5 代表有資金進場，<0.8 代表觀望 |
| 均額(百萬) | 近 20 日平均成交金額 | 越大流動性越好，新手建議優先挑 >1 億 |

**分析師提醒**：MACD 是落後指標，盤整時容易反覆金叉死叉。實務上建議搭配：
1. **基本面**：月營收年增、毛利率趨勢、EPS 是否成長（公開資訊觀測站查詢）
2. **籌碼面**：外資、投信是否同步買超；融資是否過度增加
3. **大盤環境**：加權指數本身的 MACD 方向、費半與台積電 ADR 走勢
4. **風險控管**：先設停損（例如跌破金叉當天低點或月線），單一個股不超過資金 10–20%
"""

DISCLAIMER = (
    "> ⚠️ 本報告由程式依公開資料自動產生，僅供學習與研究參考，不構成任何投資建議。"
    "技術訊號不保證未來報酬，投資前請自行判斷並承擔風險。"
)


def _fmt_pct(v):
    arrow = "🔺" if v > 0 else ("🔻" if v < 0 else "▫️")
    return f"{arrow} {v:+.2f}%"


def _dashboard(rows):
    if not rows:
        return "_（今日無法取得市場數據）_\n"
    lines = ["| 指標 | 最新 | 日漲跌 | 5日漲跌 | 資料日 |", "|---|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['last']:,.2f} | {_fmt_pct(r['d1'])} | {_fmt_pct(r['d5'])} | {r['date']} |")
    return "\n".join(lines) + "\n"


def _institutional(rows):
    if not rows:
        return "_（今日三大法人資料尚未公布或無法取得）_\n"
    lines = ["| 法人 | 買進(億) | 賣出(億) | 買賣超(億) |", "|---|---:|---:|---:|"]
    for r in rows:
        net = f"**{r['net']:+,.2f}**" if "合計" in r["name"] else f"{r['net']:+,.2f}"
        lines.append(f"| {r['name']} | {r['buy']:,.2f} | {r['sell']:,.2f} | {net} |")
    return "\n".join(lines) + "\n"


def _picks(df, limit):
    if df is None or df.empty:
        return "_今日沒有符合「低檔翻揚、MACD 轉正」條件的個股。_\n"
    lines = [
        "| # | 代號 | 名稱 | 市場 | 產業 | 收盤 | 漲跌 | 訊號 | 評分 | 區間位置 | 量比 | RSI | 站上月線 | 均額(百萬) |",
        "|---:|---|---|---|---|---:|---:|---|:---:|---:|---:|---:|:---:|---:|",
    ]
    for i, r in enumerate(df.head(limit).itertuples(), 1):
        lines.append(
            f"| {i} | {r.code} | {r.name} | {r.market} | {r.industry} | {r.close:,.2f} | {r.chg_pct:+.2f}% "
            f"| {r.signals} | {'⭐' * min(r.score, 7)} {r.score} | {r.range_pos:.0f}% | {r.vol_ratio:.2f} "
            f"| {r.rsi14:.0f} | {'✅' if r.above_ma20 else '—'} | {r.avg_value_m:,.0f} |"
        )
    return "\n".join(lines) + "\n"


def _industry_summary(df):
    if df is None or df.empty:
        return ""
    counts = df["industry"].value_counts().head(8)
    parts = [f"{k}（{v}）" for k, v in counts.items()]
    return "**訊號集中產業**：" + "、".join(parts) + "\n\n> 若同一產業多檔同時翻揚，可能代表類股輪動資金進駐，值得進一步研究該產業的基本面催化劑。\n"


def _news(sections):
    out = []
    for title, items in sections:
        out.append(f"### {title}\n")
        if not items:
            out.append("_（暫無新聞）_\n")
            continue
        for it in items:
            t = it["time"].astimezone(TPE).strftime("%m/%d %H:%M") if it["time"] else ""
            src = f" — {it['source']}" if it["source"] else ""
            out.append(f"- [{it['title']}]({it['link']}){src} `{t}`")
        out.append("")
    return "\n".join(out) + "\n"


def build(report_date, data_date, dashboard, institutional, picks, news, scanned, limit=40):
    n = 0 if picks is None else len(picks)
    parts = [
        f"# 📈 台股每日投資日報 — {report_date}\n",
        f"價格資料日：**{data_date}**｜掃描 {scanned} 檔高流動性上市櫃股票｜入選 **{n}** 檔\n",
        DISCLAIMER + "\n",
        "## 1. 市場儀表板（台股 × 國際）\n",
        _dashboard(dashboard),
        "## 2. 三大法人買賣超（上市）\n",
        _institutional(institutional),
        "## 3. 🎯 從低檔翻揚・MACD 轉正個股\n",
        "依評分高到低排序（同分時依成交金額）。\n",
        _picks(picks, limit),
        _industry_summary(picks),
        GUIDE,
        "## 4. 📰 每日必看：投資趨勢・產業資訊・國際新聞\n",
        _news(news),
        "## 5. ✅ 每日盤後檢查清單\n",
        "- [ ] 加權指數與櫃買指數今天是漲是跌？量能是放大還是萎縮？\n"
        "- [ ] 外資、投信今天站在買方還是賣方？連續幾天？\n"
        "- [ ] 費半、台積電 ADR、那斯達克昨晚表現如何？（影響明天開盤）\n"
        "- [ ] 美元/新台幣：台幣升值通常有利外資匯入、貶值則相反\n"
        "- [ ] 今日入選股中，哪些產業重複出現？是否有新聞催化？\n"
        "- [ ] 挑 1–2 檔加入觀察名單，查它的月營收與法人籌碼，寫下進場理由與停損點\n",
    ]
    return "\n".join(parts)
