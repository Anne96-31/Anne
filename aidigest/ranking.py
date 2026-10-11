"""針對「Data Engineer → AI Engineer」的相關度評分與主題標記。

中英文關鍵字並存，因為來源同時有英文媒體與中文媒體（TechOrange）。

分數 = 來源權重 + 主題關鍵字加權 + 新鮮度 + 實作型標題加分 - 噪音扣分
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .fetch import Article


@dataclass(frozen=True)
class Theme:
    key: str
    label: str          # Notion / 終端顯示用的中文標籤
    weight: float       # 對轉職目標的價值
    keywords: tuple[str, ...]
    why: str            # 規則式的「為什麼對你重要」


THEMES: tuple[Theme, ...] = (
    Theme(
        "llm_app", "LLM 應用 / RAG / Agent", 3.2,
        ("生成式 ai", "大型語言模型", "智慧代理", "代理人", "提示", "向量", "檢索", "聊天機器人",
         "rag", "retrieval-augmented", "retrieval augmented", "agent", "agentic", "prompt",
         "context engineering", "mcp", "model context protocol", "tool use", "tool calling",
         "function calling", "chatbot", "copilot", "multi-agent", "embedding", "vector database",
         "vector search", "semantic search", "reranker", "chunking", "langchain", "llamaindex"),
        "這是 AI Engineer 日常在做的事：把模型接上你的資料與工具，做成可用的產品。",
    ),
    Theme(
        "llmops", "評估 / LLMOps / 上線監控", 3.0,
        ("評估", "監控", "可觀測", "幻覺", "上線", "維運", "成本優化",
         "eval", "evaluation", "benchmark suite", "llmops", "mlops", "observability", "monitoring",
         "guardrail", "hallucination", "drift", "a/b test", "experiment", "model registry",
         "mlflow", "ci/cd", "regression test", "tracing", "cost optimization", "reliability"),
        "面試最常被問、也是 DE 最容易切入的一塊：把 AI 系統做得可量測、可回歸、可上線。",
    ),
    Theme(
        "serving", "推論 / 部署 / 效能", 2.8,
        ("推論", "部署", "微調", "量化", "算力", "晶片", "延遲", "效能",
         "inference", "serving", "vllm", "quantization", "quantized", "gpu", "cuda", "latency",
         "throughput", "kv cache", "batching", "triton", "onnx", "distillation", "fine-tune",
         "fine-tuning", "lora", "peft", "context window", "caching", "streaming response"),
        "AI Engineer 與 DS 的分水嶺：模型跑得動、跑得快、跑得便宜。",
    ),
    Theme(
        "data_platform", "資料工程 / 平台", 2.2,
        ("資料管線", "資料工程", "數據", "資料倉儲", "資料湖", "串流",
         "pipeline", "airflow", "dagster", "dbt", "spark", "kafka", "flink", "streaming",
         "lakehouse", "iceberg", "delta lake", "hudi", "warehouse", "snowflake", "bigquery",
         "duckdb", "polars", "pandas", "etl", "elt", "orchestration", "data quality",
         "data contract", "cdc", "partition", "parquet", "feature store", "data catalog"),
        "你的既有強項；把它連到 AI 情境（feature/embedding pipeline）就是你的差異化。",
    ),
    Theme(
        "architecture", "系統設計 / 大廠實戰", 2.4,
        ("架構", "實戰", "導入", "落地", "案例", "規模化", "轉型",
         "architecture", "at scale", "production", "case study", "migration", "we built",
         "how we", "lessons learned", "postmortem", "incident", "platform", "infrastructure",
         "distributed", "throughput", "cost saving", "petabyte", "billions"),
        "可以直接寫進履歷與面試故事的實戰案例，補上你缺的「AI 系統設計」語彙。",
    ),
    Theme(
        "foundation", "模型基礎 / 研究", 1.6,
        ("模型", "研究", "論文", "開源模型", "基準測試",
         "transformer", "attention", "diffusion", "reinforcement learning", "rlhf", "pretraining",
         "reasoning model", "state space", "mixture of experts", "moe", "paper", "arxiv",
         "state of the art", "sota"),
        "打底用：了解模型能力邊界，才知道系統該怎麼設計。",
    ),
    Theme(
        "career", "職涯 / 學習路徑", 2.6,
        ("職涯", "轉職", "學習", "教學", "入門", "指南", "課程", "人才", "招募",
         "career", "interview", "roadmap", "learn", "course", "tutorial", "guide", "beginner",
         "portfolio", "resume", "hiring", "job", "skills", "cheat sheet", "handbook",
         "getting started", "from scratch", "step by step"),
        "轉職路上的直接彈藥：學習資源、面試題型與技能盤點。",
    ),
    Theme(
        "tooling", "工具 / 開源專案", 1.8,
        ("工具", "開源", "發布", "推出", "套件",
         "open source", "open-source", "library", "framework", "release", "launch", "sdk",
         "api", "toolkit", "cli", "github", "version", "announcing"),
        "工具更新；挑一兩個實際裝起來玩，比讀十篇文章有效。",
    ),
)

# 標題裡出現這些字，代表是「動手做」型內容，對轉職特別有價值
HANDS_ON = ("how to", "build", "building", "implement", "tutorial", "walkthrough", "guide",
            "from scratch", "step-by-step", "step by step", "we built", "in production",
            "lessons", "deep dive", "practical")

# 純新聞 / 商業話題，對工程能力幫助小
NOISE = ("funding", "raises $", "ipo", "stock", "lawsuit", "acquisition", "partnership",
         "ceo", "layoff", "valuation", "regulation", "webinar", "sponsored", "sweepstake")


def _match_count(text: str, keywords: tuple[str, ...]) -> int:
    hits = 0
    for kw in keywords:
        pattern = r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])" if kw.isalpha() else re.escape(kw)
        if re.search(pattern, text):
            hits += 1
    return hits


def score_article(article: Article) -> Article:
    title = article.title.lower()
    body = f"{title} {article.summary.lower()}"

    score = article.source_weight
    themes: list[str] = []
    reasons: list[str] = []

    for theme in THEMES:
        title_hits = _match_count(title, theme.keywords)
        body_hits = _match_count(body, theme.keywords)
        if body_hits == 0:
            continue
        # 標題命中權重最高，內文命中遞減（最多算 3 個關鍵字，避免關鍵字堆砌灌分）
        gain = theme.weight * (1.0 * min(title_hits, 2) + 0.35 * min(body_hits - title_hits, 3))
        score += gain
        themes.append(theme.key)
        reasons.append(theme.why)

    # 交叉主題加分：同時談「資料工程」與「LLM/推論」的內容 = 你的轉職甜蜜點
    if "data_platform" in themes and ({"llm_app", "serving", "llmops"} & set(themes)):
        score += 3.0
        reasons.insert(0, "同時涵蓋資料工程與 AI 系統，正好是你從 DE 跨到 AI Engineer 的橋樑。")

    if any(k in title for k in HANDS_ON):
        score += 1.5
    if any(k in body for k in NOISE):
        score -= 2.5

    # 新鮮度：24 小時內滿分，之後線性遞減
    age = article.age_hours
    score += 2.0 if age <= 24 else max(0.0, 2.0 - (age - 24) / 24)

    article.score = round(score, 2)
    article.themes = themes
    article.reasons = reasons[:2]
    return article


def theme_label(key: str) -> str:
    for theme in THEMES:
        if theme.key == key:
            return theme.label
    return key


# 每個分類最多佔幾個名額。arXiv 一天上百篇、摘要關鍵字密度又高，
# 不設上限會整份摘要被論文洗版，對「轉職實作」的幫助反而最小。
CATEGORY_CAPS = {"core": 8, "eng": 5, "lab": 4, "practitioner": 5, "research": 1}

# 你指定的核心來源：每天至少各保留這麼多名額（有文章的話）
GUARANTEED = {"kdnuggets": 2, "tds": 2, "analyticsvidhya": 2}


def rank(articles: list[Article], max_items: int, max_per_source: int) -> list[Article]:
    scored = sorted((score_article(a) for a in articles), key=lambda a: a.score, reverse=True)

    picked: list[Article] = []
    taken: set[int] = set()
    per_source: dict[str, int] = {}
    per_category: dict[str, int] = {}

    def take(art: Article) -> None:
        picked.append(art)
        taken.add(id(art))
        per_source[art.source_key] = per_source.get(art.source_key, 0) + 1
        per_category[art.category] = per_category.get(art.category, 0) + 1

    # 第一輪：保障核心來源的名額
    for source_key, quota in GUARANTEED.items():
        for art in scored:
            if len(picked) >= max_items:
                break
            if per_source.get(source_key, 0) >= quota:
                break
            if art.source_key == source_key and id(art) not in taken:
                take(art)

    # 第二輪：其餘名額按分數填滿，同時尊重來源與分類上限
    for art in scored:
        if len(picked) >= max_items:
            break
        if id(art) in taken:
            continue
        if per_source.get(art.source_key, 0) >= max_per_source:
            continue
        if per_category.get(art.category, 0) >= CATEGORY_CAPS.get(art.category, max_items):
            continue
        take(art)

    picked.sort(key=lambda a: a.score, reverse=True)
    return picked
