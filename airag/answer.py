"""RAG 的「G」：把檢索到的文章交給 Claude，產生附引用的繁體中文回答。

三道防線，避免 LLM 亂講：
1. 檢索不到任何資料 → 直接回「資料不足」，根本不呼叫 LLM（省錢、也不給它瞎掰的機會）。
2. Prompt 規定只能根據 [S1]、[S2]… 來源回答，每個論點都要標來源編號。
3. 回答後用程式檢查引用：不存在的來源編號會被移除並記錄下來（跟 dailyai 剔除捏造連結是同一個思路）。
沒有 API key 或呼叫失敗時，退回「列出最相關的幾篇」的規則式回答，功能不會整個掛掉。
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field

import anthropic

from .index import BM25Index, Hit

log = logging.getLogger(__name__)

MODEL = os.environ.get("RAG_MODEL", "").strip() or "claude-opus-5-5"
EFFORT = os.environ.get("RAG_EFFORT", "").strip() or "medium"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
CITATION_RE = re.compile(r"\[S(\d+)\]")

SYSTEM_PROMPT = """你是使用者的「AI 學習筆記助理」。使用者是正在從 Data Engineer 轉職 AI Engineer 的台灣工程師，
這些來源是他過去每天閱讀的 AI & Data 產業摘要。

回答規則：
1. 只能根據提供的來源 [S1]、[S2]… 回答，不要使用來源以外的知識補充事實。
2. 每個論點後面標上來源編號，例如「continuous batching 可提升吞吐量 [S1]」。
3. 來源不足以回答時，把 insufficient_context 設為 true，並在 answer 說明缺了什麼，不要硬湊答案。
4. 用繁體中文（台灣用語），技術名詞保留英文；回答精簡，先給結論再補細節。
"""

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "description": "繁體中文回答，論點後標 [S#] 引用"},
        "insufficient_context": {"type": "boolean", "description": "來源不足以回答時為 true"},
        "follow_up": {
            "type": "array", "items": {"type": "string"},
            "description": "0-3 個值得接著問的問題",
        },
    },
    "required": ["answer", "insufficient_context", "follow_up"],
    "additionalProperties": False,
}


@dataclass
class Answer:
    question: str
    answer: str
    sources: list[Hit]
    generated_by: str                       # "claude:<model>" | "extractive" | "no-hits"
    insufficient_context: bool = False
    follow_up: list[str] = field(default_factory=list)
    dropped_citations: list[int] = field(default_factory=list)   # 被剔除的不存在來源編號

    def cited_sources(self) -> list[tuple[int, Hit]]:
        ids = sorted({int(n) for n in CITATION_RE.findall(self.answer)})
        return [(i, self.sources[i - 1]) for i in ids if 1 <= i <= len(self.sources)]

    def to_markdown(self) -> str:
        lines = [self.answer, ""]
        cited = self.cited_sources() or list(enumerate(self.sources, start=1))
        if cited:
            lines.append("**來源**")
            for i, hit in cited:
                c = hit.chunk
                link = f"[{c.title}]({c.url})" if c.url else c.title
                lines.append(f"- [S{i}] {link}（{c.date}{' · ' + c.source if c.source else ''}）")
        if self.follow_up:
            lines += ["", "**可以接著問**"] + [f"- {q}" for q in self.follow_up]
        lines += ["", f"*回答引擎：{self.generated_by}*"]
        return "\n".join(lines)


def build_context(hits: list[Hit]) -> str:
    blocks = []
    for i, hit in enumerate(hits, start=1):
        c = hit.chunk
        meta = " · ".join(x for x in (c.date, c.source, c.priority) if x)
        blocks.append(f"[S{i}] {c.title}（{meta}）\n{c.text}")
    return "\n\n".join(blocks)


def validate_citations(text: str, n_sources: int) -> tuple[str, list[int]]:
    """移除不存在的 [S#]（例如只給 5 篇卻引用 [S7]），回傳 (清理後文字, 被移除的編號)。"""
    dropped: list[int] = []

    def repl(m: re.Match) -> str:
        n = int(m.group(1))
        if 1 <= n <= n_sources:
            return m.group(0)
        dropped.append(n)
        return ""

    return CITATION_RE.sub(repl, text), dropped


def extractive_answer(question: str, hits: list[Hit]) -> Answer:
    lines = ["（未使用 LLM：以下是與問題最相關的筆記，請點來源閱讀）", ""]
    for i, hit in enumerate(hits, start=1):
        c = hit.chunk
        lines.append(f"- {c.title}：{c.summary} [S{i}]")
    return Answer(question, "\n".join(lines), hits, "extractive")


def call_claude(question: str, hits: list[Hit], client: anthropic.Anthropic | None = None) -> dict | None:
    client = client or anthropic.Anthropic()
    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": ANSWER_SCHEMA}},
            messages=[{
                "role": "user",
                "content": f"<sources>\n{build_context(hits)}\n</sources>\n\n問題：{question}",
            }],
            betas=[FALLBACK_BETA],
            fallbacks="default",     # 安全分類器拒答時，伺服器端自動改用替代模型重跑
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
                data = json.loads(block.text)
            except json.JSONDecodeError:
                continue
            data["_model"] = response.model
            return data
    log.error("Claude 回應中找不到可解析的 JSON。")
    return None


def answer_question(index: BM25Index, question: str, *, k: int = 5, use_llm: bool = True,
                    client: anthropic.Anthropic | None = None, **filters) -> Answer:
    hits = index.search(question, k=k, **filters)
    if not hits:
        return Answer(question, "筆記裡找不到和這個問題相關的內容，試試換個關鍵字或放寬日期範圍。",
                      [], "no-hits", insufficient_context=True)
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    if not use_llm or (client is None and not has_key):
        return extractive_answer(question, hits)

    data = call_claude(question, hits, client)
    if not data or not data.get("answer"):
        return extractive_answer(question, hits)
    text, dropped = validate_citations(data["answer"], len(hits))
    if dropped:
        log.warning("剔除不存在的引用編號：%s", dropped)
    return Answer(
        question, text, hits, f"claude:{data.get('_model', MODEL)}",
        insufficient_context=bool(data.get("insufficient_context")),
        follow_up=[q for q in data.get("follow_up", []) if q][:3],
        dropped_citations=dropped,
    )
