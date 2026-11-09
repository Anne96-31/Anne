"""用 Claude 把當日文章整理成繁體中文的「轉職導向」摘要。

用官方 anthropic SDK（repo 的 requirements.txt 已含 anthropic>=1.12）。
API 失敗或沒設 key 時會退回規則式摘要，當天的摘要不會整份開天窗。
"""

from __future__ import annotations

import json
import logging

import anthropic

from . import config, ranking
from .fetch import Article

log = logging.getLogger(__name__)

# Claude Opus 5 的安全分類器可能拒絕請求；開啟伺服器端 fallback 讓它自動改用
# 替代模型重跑，而不是把拒絕回傳給我們。
FALLBACK_BETA = "server-side-fallback-2026-07-01"

SYSTEM_PROMPT = """你是一位同時具備 Data Engineer 與 AI Engineer 實戰經驗的資深工程師，正在指導一位台灣的 Data Engineer 轉職成 AI Engineer。

這位讀者的背景與目標：
- 現況：熟悉資料管線、SQL、Spark/Airflow 這類資料工程工具。
- 目標：成為 AI Engineer（LLM 應用開發、RAG/Agent 系統、模型評估與上線維運）。
- 需求：每天用 10 分鐘掌握產業動態，並知道「這則資訊跟我的轉職有什麼關係、今天可以做什麼」。

撰寫原則：
1. 全部用繁體中文（台灣用語），技術專有名詞保留英文原文（例如 RAG、embedding、fine-tuning）。
2. 誠實：只根據我提供的標題與摘要內容判斷。資訊不足就在 one_line 註明「摘要資訊有限」，
   絕對不要編造文章沒提到的數據、結論或作者。
3. why_for_you 要具體連結到「DE → AI Engineer」的能力落差，不要寫「這很重要」這種空話。
4. action 要是今天 10–30 分鐘內做得完的具體動作（例如：用 X 工具跑一個最小範例、
   把 Y 概念寫成筆記、對照自己現有的 pipeline 想一個應用點）。
5. priority 判準：must_read = 直接補上轉職關鍵能力；skim = 有幫助但可快速掃過；
   reference = 存起來之後需要時再看。
6. 來源包含中文媒體（TechOrange 科技報橘）。中文文章的 zh_title 直接沿用原標題即可。
"""

RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "briefing": {
            "type": "string",
            "description": "今日整體重點，3-5 句繁體中文，點出今天這批文章共同透露的產業訊號。",
        },
        "learning_plan": {
            "type": "array",
            "description": "今天 30 分鐘之內可完成的 3 個學習動作，由最重要排到次要。",
            "items": {"type": "string"},
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "對應輸入文章的編號"},
                    "zh_title": {"type": "string", "description": "繁體中文標題（可意譯，20 字內）"},
                    "one_line": {"type": "string", "description": "這篇在講什麼，1-2 句"},
                    "why_for_you": {"type": "string", "description": "對 DE 轉 AI Engineer 的具體意義，1-2 句"},
                    "action": {"type": "string", "description": "今天可執行的具體學習動作，1 句"},
                    "priority": {"type": "string", "enum": ["must_read", "skim", "reference"]},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["index", "zh_title", "one_line", "why_for_you", "action", "priority", "tags"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["briefing", "learning_plan", "items"],
    "additionalProperties": False,
}

PRIORITY_LABEL = {"must_read": "必讀", "skim": "快速瀏覽", "reference": "存參考"}


def build_prompt(articles: list[Article]) -> str:
    lines = [
        f"以下是今天從 AI / Data 產業來源抓到的 {len(articles)} 篇文章。"
        "請為每一篇產出摘要，並在最後給出今日整體重點與學習計畫。\n"
    ]
    no_summary = "（此來源未提供摘要，請只依標題判斷，並在 one_line 註明摘要資訊有限）"
    for i, art in enumerate(articles, start=1):
        themes = "、".join(ranking.theme_label(t) for t in art.themes) or "未分類"
        lines.append(
            f"[{i}] 標題：{art.title}\n"
            f"    來源：{art.source_name}（{art.local_date}）\n"
            f"    自動分類：{themes}\n"
            f"    網址：{art.link}\n"
            f"    原文摘要：{art.summary[:700] or no_summary}\n"
        )
    lines.append("\n請輸出符合 schema 的 JSON，items 必須涵蓋全部 index，順序照輸入順序。")
    return "\n".join(lines)


def call_claude(articles: list[Article]) -> dict | None:
    if not config.ANTHROPIC_API_KEY:
        log.warning("未設定 ANTHROPIC_API_KEY，改用規則式摘要。")
        return None

    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={
                "effort": config.ANTHROPIC_EFFORT,
                "format": {"type": "json_schema", "schema": RESULT_SCHEMA},
            },
            messages=[{"role": "user", "content": build_prompt(articles)}],
            extra_headers={"anthropic-beta": FALLBACK_BETA},
            extra_body={"fallbacks": "default"},
        )
    except anthropic.RateLimitError as exc:
        log.error("Claude 額度用盡（SDK 已自動重試）：%s", exc)
        return None
    except anthropic.APIStatusError as exc:
        log.error("Claude API %s：%s", exc.status_code, str(exc)[:300])
        return None
    except anthropic.APIConnectionError as exc:
        log.error("Claude 連線失敗：%s", exc)
        return None

    if response.stop_reason == "refusal":
        log.error("Claude 拒絕回應：%s", response.stop_details)
        return None

    usage = response.usage
    log.info("Claude 完成（model=%s, in=%s, out=%s tokens）",
             response.model, usage.input_tokens, usage.output_tokens)

    for block in response.content:
        if block.type == "text":
            try:
                return json.loads(block.text)
            except json.JSONDecodeError:
                continue
    log.error("Claude 回應中找不到可解析的 JSON。")
    return None


def fallback_item(article: Article, index: int) -> dict:
    first = article.summary.split(". ")[0][:180] if article.summary else ""
    labels = [ranking.theme_label(t) for t in article.themes] or ["未分類"]
    priority = "must_read" if article.score >= 10 else "skim" if article.score >= 7 else "reference"
    return {
        "index": index,
        "zh_title": article.title,
        "one_line": first or "（此來源未提供摘要，請點連結閱讀原文）",
        "why_for_you": article.reasons[0] if article.reasons else "與 AI / Data 產業動態相關。",
        "action": f"花 10 分鐘掃過原文，把「{labels[0]}」相關的關鍵字記進學習清單。",
        "priority": priority,
        "tags": labels[:3],
    }


def offline_summary(articles: list[Article]) -> dict:
    items = [fallback_item(a, i) for i, a in enumerate(articles, start=1)]
    counts: dict[str, int] = {}
    for art in articles:
        for theme in art.themes:
            counts[theme] = counts.get(theme, 0) + 1
    labels = [ranking.theme_label(t) for t in sorted(counts, key=lambda k: counts[k], reverse=True)[:3]]
    focus = "、".join(labels) or "AI / Data 綜合議題"
    primary = labels[0] if labels else "AI / Data"
    return {
        "briefing": (f"（規則式整理：Claude 摘要未啟用或呼叫失敗）今天共收錄 {len(articles)} 篇，"
                     f"主題集中在 {focus}。建議先看標記為「必讀」的項目。"),
        "learning_plan": [
            f"挑一篇「{primary}」相關文章精讀，並用自己的話寫 5 行筆記。",
            "把文章中出現、你沒實作過的工具挑一個，跑一次官方 quickstart。",
            "對照你現在維護的 pipeline，寫下一個可以導入 AI 的具體切入點。",
        ],
        "items": items,
    }


def summarize(articles: list[Article], use_llm: bool = True) -> tuple[dict, bool]:
    """回傳 (摘要結果, 是否由 Claude 產生)。缺漏的項目用規則式補齊。"""
    if use_llm:
        result = call_claude(articles)
        if result and result.get("items"):
            by_index = {int(it["index"]): it for it in result["items"] if "index" in it}
            result["items"] = [by_index.get(i) or fallback_item(articles[i - 1], i)
                               for i in range(1, len(articles) + 1)]
            return result, True
    return offline_summary(articles), False
