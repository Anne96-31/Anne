"""用 Claude 產生每日商務英文課程：10 個詞彙、約 10 分鐘的商業文章、文法重點、寫作任務。"""
import logging
import os
from datetime import date

import anthropic
from pydantic import BaseModel

log = logging.getLogger(__name__)

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")

# 每天輪替的文章主題，確保商業領域多元
THEMES = [
    "Semiconductors & AI", "Central banks & interest rates", "Consumer & retail",
    "Energy transition", "Mergers & acquisitions", "Startups & venture capital",
    "Global trade & supply chains", "Leadership & management", "Marketing & branding",
    "Corporate earnings", "Banking & fintech", "Real estate", "Healthcare & biotech",
    "Workplace & talent",
]


class VocabItem(BaseModel):
    word: str
    part_of_speech: str
    meaning_zh: str
    collocations: str
    example: str


class Expression(BaseModel):
    phrase: str
    meaning_zh: str


class GrammarPair(BaseModel):
    too_direct: str
    professional: str


class Lesson(BaseModel):
    theme: str
    goals_zh: list[str]
    vocabulary: list[VocabItem]
    usage_tips_zh: list[str]
    article_title: str
    article_paragraphs: list[str]
    source_headline: str
    source_link: str
    comprehension_questions: list[str]
    key_expressions: list[Expression]
    grammar_title: str
    grammar_explanation_zh: str
    grammar_examples: list[GrammarPair]
    grammar_toolkit: str
    writing_scenario_zh: str
    writing_requirements_zh: list[str]


SYSTEM = """You are a native English-speaking business executive who is fluent in Traditional Chinese \
and an experienced Business English teacher. Your student is a Taiwanese professional who wants their \
English to sound more polished, professional and native-like. Every day you prepare one lesson.

Lesson requirements:
- goals_zh: 3 concrete learning goals for today, in Traditional Chinese.
- vocabulary: exactly 10 advanced but genuinely common business words or phrasal verbs. Each needs a \
part of speech, a Traditional Chinese meaning, 2-3 natural collocations, and one business example sentence \
with the word in **bold**. Never reuse a word from the "already learned" list.
- usage_tips_zh: 2-3 short tips in Traditional Chinese on how native speakers use some of today's words \
(common Chinglish mistakes, register, prepositions).
- Reading: an original analytical article in the style of The Economist or the Financial Times, \
850-1000 words (about 10 minutes for an advanced learner), in 7-9 paragraphs. Build it around one of the \
real headlines provided, explaining the background, the stakes and the outlook. Do not invent specific \
figures, quotes or facts beyond what the headline states; keep claims general where you are unsure. \
Use at least 7 of today's vocabulary words, each in **bold**. Put the chosen headline and its link in \
source_headline and source_link (exactly as given). If no headlines are provided, write about today's \
theme in general terms and leave source_headline and source_link empty.
- comprehension_questions: 4 questions in English.
- key_expressions: 5-6 advanced idiomatic phrases taken from the article, with Traditional Chinese meanings.
- Grammar spotlight: one topic that makes English sound more native and professional (e.g. hedging, \
nominalisation, articles, parallel structure, softening requests, cleft sentences, concise phrasing). \
Do not repeat a recent topic. Explain in Traditional Chinese, give 4 too_direct -> professional pairs, \
and a one-line toolkit of useful words or patterns.
- Writing task: a realistic workplace scenario (email, memo, meeting summary, LinkedIn post, etc.) \
related to the article, described in Traditional Chinese; requirements must ask for 100-150 words, \
using at least 4 of today's words and today's grammar point.
Never use the "|" character in any field."""


def generate(today: date, headlines, learned_words, recent_grammar, client=None) -> Lesson:
    theme = THEMES[today.toordinal() % len(THEMES)]
    news = "\n".join(f"- {h['title']} | {h['link']}" for h in headlines) or "- (no headlines available)"
    prompt = f"""Date: {today.isoformat()}
Today's theme: {theme}

Real business headlines from the past day (pick the one that best fits today's theme; \
if none fits, pick the most significant one):
{news}

Already learned vocabulary (do not reuse): {", ".join(learned_words) or "(none yet)"}
Recent grammar topics (do not repeat): {", ".join(recent_grammar) or "(none yet)"}

Prepare today's lesson."""

    client = client or anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_format=Lesson,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude 拒絕產生課程：{response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("課程內容超過 max_tokens 被截斷")
    lesson = response.parsed_output
    words = sum(len(p.split()) for p in lesson.article_paragraphs)
    log.info("課程已產生：%s｜%d 個詞彙｜文章 %d 字", lesson.theme, len(lesson.vocabulary), words)
    return lesson


def _row(*cells):
    return "| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |"


def to_markdown(lesson: Lesson, day: int, today: date) -> str:
    vocab_rows = [_row(i, f"**{v.word}**", v.part_of_speech, v.meaning_zh, v.collocations, v.example)
                  for i, v in enumerate(lesson.vocabulary, 1)]
    grammar_rows = [_row(g.too_direct, g.professional) for g in lesson.grammar_examples]
    lines = [
        f"_Day {day}｜{today.isoformat()}｜{lesson.theme}_",
        "",
        "# 🎯 本日學習目標",
        *[f"- [ ] {g}" for g in lesson.goals_zh],
        "",
        "## ✅ 今日任務",
        "- [ ] ① 熟記 10 個詞彙（約 8 分鐘）",
        "- [ ] ② 閱讀文章並回答 4 題理解問題（約 10–12 分鐘）",
        "- [ ] ③ 讀懂今日文法重點（約 3 分鐘）",
        "- [ ] ④ 完成 100–150 字短文，貼給 Claude 批改（約 15 分鐘）",
        "",
        "# ① Vocabulary：今日 10 詞",
        "| # | 詞彙 | 詞性 | 中文 | 常用搭配 | 商務例句 |",
        "|---|---|---|---|---|---|",
        *vocab_rows,
        "",
        "### 🎯 母語者用法提醒",
        *[f"- {t}" for t in lesson.usage_tips_zh],
        "",
        "# ② Reading：商業文章（約 10 分鐘）",
        f"## {lesson.article_title}",
        f"> 練習用原創分析文章，靈感來自新聞：[{lesson.source_headline}]({lesson.source_link})"
        if lesson.source_link else "> 練習用原創分析文章，非真實新聞報導",
        *lesson.article_paragraphs,
        "",
        "### 📝 閱讀理解（請用英文回答）",
        *[f"{i}. {q}" for i, q in enumerate(lesson.comprehension_questions, 1)],
        "",
        "### 💎 值得收藏的進階表達",
        *[f"- **{e.phrase}** = {e.meaning_zh}" for e in lesson.key_expressions],
        "",
        f"# ③ Grammar Spotlight：{lesson.grammar_title}",
        lesson.grammar_explanation_zh,
        "| 太直接 ❌ | 專業版 ✅ |",
        "|---|---|",
        *grammar_rows,
        "",
        f"常用工具：{lesson.grammar_toolkit}",
        "",
        "# ④ Writing Task：今日短文（100–150 字）",
        f"**情境：** {lesson.writing_scenario_zh}",
        *[f"- {r}" for r in lesson.writing_requirements_zh],
        "",
        "## ✍️ 我的短文",
        "（寫在這裡，完成後貼給 Claude 批改）",
        "",
        "## 🔁 批改後的 Native 版本",
        "（把 Claude 的改寫貼在這裡，方便日後複習）",
    ]
    return "\n".join(lines)
