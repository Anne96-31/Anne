"""檢索評估：用一份「問題 → 正確文章」的黃金測試集，量化檢索品質。

為什麼用凍結的語料（airag/eval/corpus/）：digests/ 只保留 30 天，舊文章會被刪掉，
如果直接拿 digests/ 評估，分數會因為資料變動而飄，無法比較「改了程式之後是不是更好」。

指標：
- hit@k：正確答案有沒有出現在前 k 名（有 = 1，沒有 = 0），取平均。
- MRR（Mean Reciprocal Rank）：第一個正確答案排第幾名就得 1/名次，再取平均。
  排第 1 名得 1.0、第 2 名得 0.5、沒進前 k 名得 0。比 hit@k 更在意「排得夠不夠前面」。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

from .corpus import load_corpus
from .index import BM25Index, IndexConfig

EVAL_DIR = Path(__file__).resolve().parent / "eval"
DEFAULT_QUESTIONS = EVAL_DIR / "questions.json"
DEFAULT_CORPUS = EVAL_DIR / "corpus"


@dataclass(frozen=True)
class EvalResult:
    name: str
    hit_at_1: float
    hit_at_k: float
    mrr: float
    k: int
    misses: tuple[str, ...]           # 前 k 名都沒找到正確答案的問題，方便除錯

    def row(self) -> str:
        return (f"| {self.name} | {self.hit_at_1:.2f} | {self.hit_at_k:.2f} | {self.mrr:.3f} |")


def load_questions(path: Path = DEFAULT_QUESTIONS) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate(index: BM25Index, questions: list[dict], *, k: int = 5, name: str = "default") -> EvalResult:
    hits1 = hitsk = rr_sum = 0.0
    misses = []
    for q in questions:
        relevant = {r["url"] for r in q["relevant"]}
        ranked = [h.chunk.url for h in index.search(q["question"], k=k, kind="article")]
        rank = next((i for i, url in enumerate(ranked, start=1) if url in relevant), None)
        if rank is None:
            misses.append(q["question"])
            continue
        hitsk += 1
        hits1 += rank == 1
        rr_sum += 1 / rank
    n = len(questions) or 1
    return EvalResult(name, hits1 / n, hitsk / n, rr_sum / n, k, tuple(misses))


# 消融實驗：一次關掉一個設計，看分數掉多少 → 證明每個設計都有用（或沒用）
ABLATIONS: list[tuple[str, dict]] = [
    ("預設（中文 bigram + 中英同義詞）", {}),
    ("拿掉中英同義詞擴充", {"expand_synonyms": False}),
    ("加上標題/tag 加權", {"field_boost": True}),
    ("中文改用單字（不用 bigram）", {"cjk_bigrams": False}),
]


def run_ablation(corpus_dir: Path = DEFAULT_CORPUS, questions_path: Path = DEFAULT_QUESTIONS,
                 *, k: int = 5, difficulty: str | None = None) -> list[EvalResult]:
    """difficulty="easy"：題目用詞接近標題；"hard"：換句話說、中英交叉，比較接近真實提問。"""
    chunks = load_corpus(corpus_dir)
    questions = load_questions(questions_path)
    if difficulty:
        questions = [q for q in questions if q.get("difficulty") == difficulty]
    base = IndexConfig()
    return [evaluate(BM25Index(chunks, replace(base, **overrides)), questions, k=k, name=name)
            for name, overrides in ABLATIONS]


def format_table(results: list[EvalResult]) -> str:
    k = results[0].k if results else 5
    lines = [f"| 設定 | hit@1 | hit@{k} | MRR |", "|---|---|---|---|"]
    lines += [r.row() for r in results]
    return "\n".join(lines)
