"""把摘要結果轉成 Notion blocks 與 Markdown。"""

from __future__ import annotations

from datetime import datetime

from . import notion as nc
from . import ranking
from . import sources as src
from .fetch import Article
from .summarize import PRIORITY_LABEL

SECTIONS = [
    ("must_read", "🔥 今日必讀", "直接補上你轉職缺的能力"),
    ("skim", "👀 值得快速瀏覽", "掃過標題與重點即可"),
    ("reference", "🗂️ 存起來參考", "之後需要時再回頭看"),
]


def _pair(articles: list[Article], result: dict) -> list[tuple[Article, dict]]:
    return [(articles[item["index"] - 1], item)
            for item in result["items"]
            if 1 <= item.get("index", 0) <= len(articles)]


def _source_stats(articles: list[Article]) -> str:
    counts: dict[str, int] = {}
    for art in articles:
        counts[art.source_name] = counts.get(art.source_name, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return "、".join(f"{name} × {n}" for name, n in ordered)


# --------------------------------------------------------------------------
# Notion
# --------------------------------------------------------------------------

def build_blocks(articles: list[Article], result: dict, *, generated_by: str,
                 scanned: int, now: datetime) -> list[dict]:
    pairs = _pair(articles, result)
    blocks: list[dict] = [
        nc.callout(result.get("briefing", ""), "💡"),
    ]

    for priority, title, hint in SECTIONS:
        group = [(a, it) for a, it in pairs if it.get("priority") == priority]
        if not group:
            continue
        blocks.append(nc.heading(f"{title}（{len(group)}）", 2))
        blocks.append(nc.paragraph(nc.rich_text(hint, italic=True, color="gray")))
        for art, item in group:
            head = (
                nc.rich_text(item.get("zh_title") or art.title, bold=True, link=art.link)
                + nc.rich_text(f"  · {art.source_name}", color="gray")
            )
            children = [
                nc.paragraph(nc.rich_text("內容：", bold=True) + nc.rich_text(item.get("one_line", ""))),
                nc.paragraph(nc.rich_text("對你的意義：", bold=True) + nc.rich_text(item.get("why_for_you", ""))),
                nc.paragraph(nc.rich_text("今天可以做：", bold=True) + nc.rich_text(item.get("action", ""))),
                nc.paragraph(
                    nc.rich_text("　".join(f"#{t}" for t in item.get("tags", [])[:4]), code=True, color="gray")
                    + nc.rich_text(f"　原文：{art.title}", color="gray")
                ),
            ]
            blocks.append(nc.bullet(head, children))

    plan = result.get("learning_plan", [])
    if plan:
        blocks.append(nc.heading("🎯 今天的 30 分鐘學習計畫", 2))
        for step in plan:
            blocks.append(nc.numbered(step))

    blocks.append(nc.divider())
    blocks.append(nc.heading("📊 本次抓取資訊", 3))
    blocks.append(nc.paragraph(f"掃描 {scanned} 篇，收錄 {len(pairs)} 篇。來源分布：{_source_stats(articles)}"))
    for manual in src.manual_sources():
        blocks.append(nc.paragraph(
            nc.rich_text("⚠️ ", color="gray")
            + nc.rich_text(manual["name"], link=manual["site"])
            + nc.rich_text(f"：{manual.get('note', '需人工瀏覽')}", color="gray")
        ))
    blocks.append(nc.paragraph(nc.rich_text(
        f"由 ai-data-digest 於 {now:%Y-%m-%d %H:%M} 自動產生 · 摘要引擎：{generated_by}",
        italic=True, color="gray",
    )))
    return blocks


# --------------------------------------------------------------------------
# Markdown（本機備份 / 終端輸出）
# --------------------------------------------------------------------------

def build_markdown(articles: list[Article], result: dict, *, generated_by: str,
                   scanned: int, now: datetime, title: str) -> str:
    pairs = _pair(articles, result)
    lines = [f"# {title}", "", f"> {result.get('briefing', '')}", ""]

    for priority, section_title, hint in SECTIONS:
        group = [(a, it) for a, it in pairs if it.get("priority") == priority]
        if not group:
            continue
        lines += [f"## {section_title}（{len(group)}）", "", f"*{hint}*", ""]
        for art, item in group:
            tags = " ".join(f"`#{t}`" for t in item.get("tags", [])[:4])
            lines += [
                f"### [{item.get('zh_title') or art.title}]({art.link})",
                f"*{art.source_name} · {art.published:%Y-%m-%d} · 相關度 {art.score} · {PRIORITY_LABEL.get(priority, priority)}*",
                "",
                f"- **內容**：{item.get('one_line', '')}",
                f"- **對你的意義**：{item.get('why_for_you', '')}",
                f"- **今天可以做**：{item.get('action', '')}",
                f"- **原文標題**：{art.title}",
                f"- {tags}",
                "",
            ]

    plan = result.get("learning_plan", [])
    if plan:
        lines += ["## 🎯 今天的 30 分鐘學習計畫", ""]
        lines += [f"{i}. {step}" for i, step in enumerate(plan, start=1)]
        lines.append("")

    lines += [
        "---",
        "",
        f"掃描 {scanned} 篇，收錄 {len(pairs)} 篇。來源分布：{_source_stats(articles)}",
        "",
    ]
    for manual in src.manual_sources():
        lines.append(f"> ⚠️ [{manual['name']}]({manual['site']})：{manual.get('note', '需人工瀏覽')}")
        lines.append("")
    lines.append(f"*由 ai-data-digest 於 {now:%Y-%m-%d %H:%M} 自動產生 · 摘要引擎：{generated_by}*")
    return "\n".join(lines)


def build_console(articles: list[Article], result: dict) -> str:
    pairs = _pair(articles, result)
    lines = [result.get("briefing", ""), ""]
    for priority, section_title, _ in SECTIONS:
        group = [(a, it) for a, it in pairs if it.get("priority") == priority]
        if not group:
            continue
        lines.append(f"── {section_title} ──")
        for art, item in group:
            themes = "/".join(ranking.theme_label(t) for t in art.themes[:2])
            lines.append(f"  [{art.score:>5}] {item.get('zh_title') or art.title}")
            lines.append(f"          {art.source_name} · {themes}")
            lines.append(f"          {art.link}")
        lines.append("")
    return "\n".join(lines)
