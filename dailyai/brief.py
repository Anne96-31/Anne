"""用 Claude 把當天的 AI 新聞整理成繁體中文快報：重點摘要、分類新聞、後續觀察、術語小教室。"""
import logging
import os
from datetime import date

import anthropic
from pydantic import BaseModel

log = logging.getLogger(__name__)

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")

CATEGORIES = ["🚀 模型與產品", "💰 產業與投資", "🔬 研究與開源", "🏛️ 政策與監管", "🖥️ 晶片與算力", "🇹🇼 台灣 AI"]


class NewsItem(BaseModel):
    category: str
    title_zh: str
    summary_zh: str
    why_it_matters_zh: str
    source_title: str
    source_link: str
    source_name: str


class Term(BaseModel):
    term: str
    explanation_zh: str


class Brief(BaseModel):
    headline_zh: str
    takeaways_zh: list[str]
    items: list[NewsItem]
    watch_list_zh: list[str]
    term: Term
    tags: list[str]


SYSTEM = f"""You are a senior AI industry analyst who writes a daily AI briefing in Traditional Chinese \
(Taiwan usage) for a busy Taiwanese professional. You are given real headlines from the past day.

Briefing requirements:
- headline_zh: one sentence (under 40 characters) capturing the single most important development today.
- takeaways_zh: exactly 3 bullet-style key takeaways.
- items: pick the 6-10 most significant and distinct stories. Merge headlines about the same event into one \
item. Skip clickbait, listicles, stock-tip articles and anything not really about AI. Avoid stories already \
covered on previous days (list given) unless there is a genuinely new development.
  - category: exactly one of {", ".join(CATEGORIES)}.
  - title_zh: a concise Traditional Chinese title.
  - summary_zh: 2-3 sentences explaining what happened. Only use facts stated in or directly implied by the \
headline; do not invent numbers, quotes, dates or details. Use cautious wording where unsure.
  - why_it_matters_zh: one sentence on why it matters (impact on industry, users, or Taiwan supply chain).
  - source_title, source_link, source_name: copy exactly from the chosen headline line.
- watch_list_zh: 2-3 things worth watching in the coming days.
- term: one AI concept or jargon word that appears in today's news, explained plainly in Traditional Chinese \
for a non-engineer (2-3 sentences). Do not repeat a recent term (list given).
- tags: 3-6 short keywords (company, product or topic names) for filtering.
Never use the "|" character in any field."""


def generate(today: date, headlines, covered_titles, recent_terms, client=None) -> Brief:
    news = "\n".join(f"- {h['title']} | {h['link']} | {h.get('source', '')}" for h in headlines) \
        or "- (no headlines available)"
    prompt = f"""Date: {today.isoformat()}

Headlines from the past day (title | link | source):
{news}

Stories covered on previous days: {"; ".join(covered_titles) or "(none)"}
Recent terms (do not repeat): {", ".join(recent_terms) or "(none)"}

Write today's AI briefing."""

    client = client or anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_format=Brief,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude 拒絕產生快報：{response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("快報內容超過 max_tokens 被截斷")
    brief = response.parsed_output
    # 只保留來源確實出現在輸入中的新聞，避免模型捏造連結
    links = {h["link"] for h in headlines}
    dropped = [i.title_zh for i in brief.items if i.source_link not in links]
    if dropped:
        log.warning("略過來源不明的 %d 則：%s", len(dropped), "、".join(dropped))
        brief.items = [i for i in brief.items if i.source_link in links]
    log.info("快報已產生：%d 則新聞｜%s", len(brief.items), brief.headline_zh)
    return brief


def to_markdown(brief: Brief, today: date) -> str:
    lines = [
        f"_{today.isoformat()}｜共 {len(brief.items)} 則｜由 Claude 依當日新聞標題整理，細節請以原文為準_",
        "",
        f"# 📌 {brief.headline_zh}",
        *[f"- {t}" for t in brief.takeaways_zh],
        "",
    ]
    order = {c: n for n, c in enumerate(CATEGORIES)}
    for cat in sorted({i.category for i in brief.items}, key=lambda c: order.get(c, len(order))):
        lines.append(f"# {cat}")
        for i in (x for x in brief.items if x.category == cat):
            lines += [
                f"## {i.title_zh}",
                i.summary_zh,
                f"> 💡 {i.why_it_matters_zh}",
                f"- 來源：[{i.source_title}]({i.source_link})" + (f"（{i.source_name}）" if i.source_name else ""),
                "",
            ]
    lines += [
        "# 👀 後續觀察",
        *[f"- {w}" for w in brief.watch_list_zh],
        "",
        f"# 📖 AI 術語小教室：{brief.term.term}",
        brief.term.explanation_zh,
    ]
    return "\n".join(lines)
