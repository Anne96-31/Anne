"""中英混合的 BM25 檢索。

為什麼先用 BM25 而不是 embedding：
- 語料小（30 天 × 約 14 則 ≈ 400 個 chunk），而且滿滿專有名詞（RAG、MCP、vLLM、Databricks），
  詞彙比對本來就很強；BM25 不需要模型、不需要 GPU、結果可解釋（看得到命中了哪些詞）。
- 中文沒有空白斷詞，用「字元 bigram」處理，不用額外裝斷詞套件。
- 中英跨語言靠一張小型同義詞表做 query expansion（問「檢索增強」也找得到寫 RAG 的文章）。
- Retriever 介面保持簡單（search(query, k, **filters) -> list[Hit]），之後要加 dense/hybrid 只換這一層。
用 `python -m airag eval --ablation` 可以量化每個設計（bigram、同義詞、欄位加權）各自貢獻多少。
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import date as Date
from pathlib import Path
from typing import Iterable

from .corpus import Chunk, digest_files, load_corpus

CJK_RUN_RE = re.compile(r"[㐀-䶿一-鿿]+")
WORD_RE = re.compile(r"[a-z0-9]+")

EN_STOPWORDS = frozenset("""
a an and are as at be by for from has have how in is it its of on or that the this to was were
what when which who why will with you your we our can do does not into about than then them they
""".split())

# 中英同義詞群組：查詢命中任一詞，就把同群組其他詞以較低權重加進查詢。
SYNONYM_GROUPS: tuple[tuple[str, ...], ...] = (
    ("rag", "檢索增強", "retrieval augmented generation", "retrieval augmented"),
    ("agent", "agentic", "代理", "智慧代理", "代理人"),
    ("multi agent", "多代理", "多 agent"),
    ("eval", "evaluation", "評估", "測試集", "benchmark"),
    ("embedding", "向量", "vector", "嵌入"),
    ("fine tuning", "finetuning", "微調"),
    ("llm", "大型語言模型", "語言模型"),
    ("inference", "推論"),
    ("cost", "成本", "費用"),
    ("latency", "延遲"),
    ("prompt", "提示"),
    ("pipeline", "管線", "etl"),
    ("data quality", "資料品質"),
    ("governance", "治理"),
    ("security", "資安"),
    ("mcp", "model context protocol"),
    ("knowledge graph", "知識圖譜", "graphrag"),
    ("monitoring", "observability", "監控", "可觀測"),
    ("hallucination", "幻覺"),
    ("cache", "caching", "快取"),
    ("gpu", "算力"),
    ("career", "職涯", "轉職"),
    ("open source", "開源", "open weight"),
    ("search", "搜尋"),
    ("streaming", "串流"),
)

PRIORITIES = ("must_read", "skim", "reference")


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).lower()


def _stem(word: str) -> str:
    """極簡英文詞形還原：agents→agent、llms→llm。夠用就好，不引入 NLTK。"""
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokenize(text: str, *, cjk_bigrams: bool = True) -> list[str]:
    """英文：小寫 + 去停用詞 + 簡單去複數；中文：連續漢字切成字元 bigram（單字則保留 unigram）。"""
    text = _normalize(text)
    tokens: list[str] = []
    for run in CJK_RUN_RE.findall(text):
        if not cjk_bigrams or len(run) == 1:
            tokens.extend(run)
        else:
            tokens.extend(run[i:i + 2] for i in range(len(run) - 1))
    for word in WORD_RE.findall(CJK_RUN_RE.sub(" ", text)):
        if word not in EN_STOPWORDS:
            tokens.append(_stem(word))
    return tokens


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float
    matched_terms: tuple[str, ...]      # 可解釋性：這筆是因為哪些詞被找到

    def to_dict(self, snippet_chars: int = 180) -> dict:
        c = self.chunk
        snippet = c.summary if len(c.summary) <= snippet_chars else c.summary[:snippet_chars] + "…"
        return {
            "chunk_id": c.chunk_id, "date": c.date, "kind": c.kind, "title": c.title,
            "url": c.url, "source": c.source, "priority": c.priority, "tags": list(c.tags),
            "score": round(self.score, 4), "matched_terms": list(self.matched_terms),
            "snippet": snippet,
        }


@dataclass(frozen=True)
class IndexConfig:
    k1: float = 1.5
    b: float = 0.75
    cjk_bigrams: bool = True
    expand_synonyms: bool = True
    expansion_weight: float = 0.5
    # 標題與 tag 權重加倍。直覺上有用，但評估顯示會讓「用詞不同」的提問排名變差，所以預設關閉。
    field_boost: bool = False


class BM25Index:
    def __init__(self, chunks: Iterable[Chunk], config: IndexConfig | None = None):
        self.config = config or IndexConfig()
        self.chunks: list[Chunk] = list(chunks)
        self._tf: list[Counter[str]] = []
        self._len: list[int] = []
        df: Counter[str] = Counter()
        for chunk in self.chunks:
            tf = Counter(self._doc_tokens(chunk))
            self._tf.append(tf)
            self._len.append(sum(tf.values()))
            df.update(tf.keys())
        n = len(self.chunks)
        self._avg_len = (sum(self._len) / n) if n else 0.0
        # BM25+ 風格的平滑 IDF，確保永遠為正
        self._idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self._groups = [
            [tuple(self._tok(term)) for term in group] for group in SYNONYM_GROUPS
        ]

    # ------------------------------------------------------------------ 建索引

    def _tok(self, text: str) -> list[str]:
        return tokenize(text, cjk_bigrams=self.config.cjk_bigrams)

    def _doc_tokens(self, c: Chunk) -> list[str]:
        boost = 2 if self.config.field_boost else 1
        tokens = self._tok(c.title) * boost + self._tok(" ".join(c.tags)) * boost
        for part in (c.original_title, c.summary, c.why, c.action):
            tokens += self._tok(part)
        return tokens

    # ------------------------------------------------------------------ 查詢

    def query_terms(self, query: str) -> dict[str, float]:
        """把查詢轉成 {term: 權重}；同義詞擴充的詞權重較低。"""
        base = self._tok(query)
        weights: dict[str, float] = {t: 1.0 for t in base}
        if not self.config.expand_synonyms:
            return weights
        present = set(base)
        for group in self._groups:
            if any(toks and set(toks) <= present for toks in group):
                for toks in group:
                    for t in toks:
                        weights.setdefault(t, self.config.expansion_weight)
        return weights

    def search(
        self,
        query: str,
        k: int = 5,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        priority: str | Iterable[str] | None = None,
        tag: str | None = None,
        source: str | None = None,
        kind: str | None = None,
        recency_weight: float = 0.0,
    ) -> list[Hit]:
        terms = self.query_terms(query)
        if not terms or k <= 0:
            return []
        priorities = {priority} if isinstance(priority, str) else set(priority or ())
        unknown = priorities - set(PRIORITIES)
        if unknown:
            raise ValueError(f"priority 只能是 {PRIORITIES}，收到 {sorted(unknown)}")
        for label, value in (("date_from", date_from), ("date_to", date_to)):
            if value:
                Date.fromisoformat(value)            # 格式錯誤直接丟 ValueError
        tag_l = _normalize(tag) if tag else None
        source_l = _normalize(source) if source else None

        dates = [c.date for c in self.chunks]
        newest = max(dates, default="")
        oldest = min(dates, default="")
        span = max((Date.fromisoformat(newest) - Date.fromisoformat(oldest)).days, 1) if newest else 1

        k1, b = self.config.k1, self.config.b
        hits: list[Hit] = []
        for i, chunk in enumerate(self.chunks):
            if date_from and chunk.date < date_from:
                continue
            if date_to and chunk.date > date_to:
                continue
            if priorities and chunk.priority not in priorities:
                continue
            if kind and chunk.kind != kind:
                continue
            if tag_l and not any(tag_l in _normalize(t) for t in chunk.tags):
                continue
            if source_l and source_l not in _normalize(chunk.source):
                continue
            tf, length = self._tf[i], self._len[i]
            score, matched = 0.0, []
            for term, weight in terms.items():
                f = tf.get(term)
                if not f:
                    continue
                norm = k1 * (1 - b + b * length / self._avg_len) if self._avg_len else k1
                score += weight * self._idf[term] * f * (k1 + 1) / (f + norm)
                matched.append(term)
            if score <= 0:
                continue
            if recency_weight:
                age = (Date.fromisoformat(newest) - Date.fromisoformat(chunk.date)).days
                score *= 1 + recency_weight * (1 - age / span)
            hits.append(Hit(chunk, score, tuple(matched)))
        hits.sort(key=lambda h: (-h.score, h.chunk.date), reverse=False)
        return hits[:k]


# ---------------------------------------------------------------------- 快取載入

_CACHE: dict[tuple, BM25Index] = {}


def _fingerprint(directory: Path) -> tuple:
    return tuple((p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in digest_files(directory))


def load_index(directory: Path, config: IndexConfig | None = None) -> BM25Index:
    """依檔案指紋快取索引：MCP server 長時間執行時，每日新摘要進來會自動重建。"""
    directory = Path(directory)
    key = (str(directory.resolve()), _fingerprint(directory), config or IndexConfig())
    if key not in _CACHE:
        _CACHE.clear()
        _CACHE[key] = BM25Index(load_corpus(directory), config)
    return _CACHE[key]
