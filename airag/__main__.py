"""命令列介面。

    python -m airag search "RAG 評估"            # 只檢索，不用 API key
    python -m airag search "MCP" --from 2026-11-10 --priority must_read
    python -m airag ask "最近有哪些 MCP 的實際案例？"   # 有 ANTHROPIC_API_KEY 才會用 Claude 生成
    python -m airag ask "..." --no-llm            # 強制不呼叫 LLM
    python -m airag eval                          # 在凍結語料上跑檢索評估
    python -m airag eval --ablation --difficulty hard
    python -m airag stats                         # 語料統計
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from pathlib import Path

from . import evaluate
from .answer import answer_question
from .index import PRIORITIES, load_index
from .mcp_server import DEFAULT_DIGEST_DIR


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m airag", description="AI 學習筆記 RAG")
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIGEST_DIR, help="摘要資料夾（預設 digests/）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_filters(p: argparse.ArgumentParser) -> None:
        p.add_argument("-k", type=int, default=5)
        p.add_argument("--from", dest="date_from")
        p.add_argument("--to", dest="date_to")
        p.add_argument("--priority", choices=PRIORITIES)
        p.add_argument("--tag")

    p_search = sub.add_parser("search", help="檢索相關筆記")
    p_search.add_argument("query")
    add_filters(p_search)

    p_ask = sub.add_parser("ask", help="檢索 + 生成附引用的回答")
    p_ask.add_argument("question")
    p_ask.add_argument("--no-llm", action="store_true")
    add_filters(p_ask)

    p_eval = sub.add_parser("eval", help="檢索評估（hit@k、MRR）")
    p_eval.add_argument("-k", type=int, default=5)
    p_eval.add_argument("--ablation", action="store_true", help="逐一關掉設計，比較分數")
    p_eval.add_argument("--difficulty", choices=["easy", "hard"])

    sub.add_parser("stats", help="語料統計")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stderr)

    if args.cmd == "eval":
        results = evaluate.run_ablation(k=args.k, difficulty=args.difficulty)
        if not args.ablation:
            results = results[:1]
        print(evaluate.format_table(results))
        if results[0].misses:
            print("\n前 k 名沒找到正確答案的問題：")
            for q in results[0].misses:
                print(f"- {q}")
        return 0

    index = load_index(args.dir)
    if args.cmd == "stats":
        articles = [c for c in index.chunks if c.kind == "article"]
        dates = sorted({c.date for c in index.chunks})
        print(f"chunk：{len(index.chunks)}（文章 {len(articles)}、每日重點 {len(index.chunks) - len(articles)}）")
        if dates:
            print(f"日期範圍：{dates[0]} ~ {dates[-1]}（{len(dates)} 天）")
        print("最常見標籤：" + "、".join(f"{t}×{n}" for t, n in
                                     Counter(t for c in articles for t in c.tags).most_common(10)))
        return 0

    filters = {"date_from": args.date_from, "date_to": args.date_to,
               "priority": args.priority, "tag": args.tag}
    if args.cmd == "search":
        hits = index.search(args.query, k=args.k, **filters)
        if not hits:
            print("找不到相關筆記。")
        for rank, hit in enumerate(hits, start=1):
            c = hit.chunk
            print(f"{rank}. [{hit.score:.2f}] {c.title}  ({c.date}{' · ' + c.source if c.source else ''})")
            if c.url:
                print(f"   {c.url}")
            print(f"   命中詞：{', '.join(hit.matched_terms[:8])}")
        return 0

    result = answer_question(index, args.question, k=args.k, use_llm=not args.no_llm, **filters)
    print(result.to_markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
