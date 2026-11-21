"""airag 的單元測試：不碰網路、不需要 API key。"""

import asyncio
import json
from types import SimpleNamespace

import pytest

from airag import answer, evaluate
from airag.corpus import Chunk, load_corpus, parse_digest
from airag.index import BM25Index, tokenize

SAMPLE = """# AI & Data 每日摘要 2026-11-17（二）

> 今天的重點是 Agent 與 RAG 評估。

## 🔥 今日必讀（2）

*直接補上你轉職缺的能力*

### [MoEngage 用 MCP 打造行銷 agent](https://example.com/moengage)
*AWS Machine Learning Blog · 2026-11-16 · 相關度 10.27 · 必讀*

- **內容**：把既有 API 包成 MCP tools，維持多租戶資料隔離。
- **對你的意義**：既有 API → MCP tool → agent。
- **今天可以做**：寫一份 MCP tool schema 草稿。
- **原文標題**：How MoEngage built agentic customer engagement
- `#MCP` `#Agent` `#多租戶`

### [本地 LLM 的 RAG 評估](https://example.com/local-rag)
*Towards Data Science · 2026-11-16 · 相關度 8.76 · 必讀*

- **內容**：比較五種設定的檢索與回答品質。
- **對你的意義**：可複製的評估實驗設計。
- **今天可以做**：設計 10 題測試集。
- **原文標題**：Local LLMs Handle Textbook RAG but Fail on New Research Papers
- `#RAG` `#評估`

## 👀 值得快速瀏覽（1）

### [Spark 與 Flink 怎麼選](https://example.com/spark-flink)
*Databricks Blog · 2026-11-15 · 相關度 7.1 · 快速瀏覽*

- **內容**：多數團隊選 Spark 較合適。
- `#資料工程` `#串流`

## 🎯 今天的 30 分鐘學習計畫

1. 讀 [1]。

---

> ⚠️ [Uber Engineering Blog](https://example.com/uber)：官方無 RSS
"""


def chunk(title, *, date="2026-11-10", summary="", tags=(), priority="must_read", url=None, kind="article"):
    return Chunk(chunk_id=f"{date}:{title}", date=date, kind=kind, title=title,
                 url=url or f"https://example.com/{abs(hash(title))}", priority=priority,
                 summary=summary, tags=tuple(tags))


# ---------- 切塊 ----------

def test_parse_digest_extracts_articles_and_briefing():
    chunks = parse_digest(SAMPLE)
    kinds = [c.kind for c in chunks]
    assert kinds.count("briefing") == 1 and kinds.count("article") == 3
    moe = next(c for c in chunks if "MoEngage" in c.title)
    assert moe.date == "2026-11-17"
    assert moe.url == "https://example.com/moengage"
    assert moe.source == "AWS Machine Learning Blog"
    assert moe.priority == "must_read" and moe.relevance == 10.27
    assert moe.tags == ("MCP", "Agent", "多租戶")
    assert moe.original_title.startswith("How MoEngage")
    assert "https://" not in moe.text            # URL 不進索引
    spark = next(c for c in chunks if "Spark" in c.title)
    assert spark.priority == "skim"


def test_parse_digest_ignores_warning_quote_as_briefing():
    briefing = next(c for c in parse_digest(SAMPLE) if c.kind == "briefing")
    assert "Agent 與 RAG" in briefing.summary


def test_load_corpus_dedupes_same_url_keeping_latest(tmp_path):
    (tmp_path / "2026-11-16.md").write_text(SAMPLE.replace("2026-11-17", "2026-11-16"), encoding="utf-8")
    (tmp_path / "2026-11-17.md").write_text(SAMPLE, encoding="utf-8")
    (tmp_path / "latest.md").write_text(SAMPLE, encoding="utf-8")          # 不該被讀進來
    corpus = load_corpus(tmp_path)
    moe = [c for c in corpus if c.url == "https://example.com/moengage"]
    assert len(moe) == 1 and moe[0].date == "2026-11-17"
    assert sum(c.kind == "briefing" for c in corpus) == 2


def test_real_digests_parse_one_chunk_per_heading():
    corpus_dir = evaluate.DEFAULT_CORPUS
    headings = sum(p.read_text(encoding="utf-8").count("\n### [") for p in corpus_dir.glob("*.md"))
    articles = [c for c in load_corpus(corpus_dir) if c.kind == "article"]
    assert headings > 0 and len(articles) <= headings          # 少於代表有跨天重複 URL 被去重
    assert all(c.url.startswith("http") and c.source for c in articles)


# ---------- 斷詞與檢索 ----------

def test_tokenize_mixes_cjk_bigrams_and_english():
    tokens = tokenize("用 RAG 建立 Agents 的評估")
    assert {"rag", "agent", "建立", "評估"} <= set(tokens)
    assert "the" not in tokenize("the agent")
    assert tokenize("評", cjk_bigrams=True) == ["評"]


def test_search_ranks_relevant_document_first():
    idx = BM25Index([
        chunk("vLLM continuous batching 提升吞吐量"),
        chunk("Spark 與 Flink 的選擇"),
        chunk("MCP server 設計模式", tags=["MCP"]),
    ])
    hits = idx.search("MCP 怎麼設計")
    assert hits[0].chunk.title == "MCP server 設計模式"
    assert "mcp" in hits[0].matched_terms


def test_synonym_expansion_bridges_chinese_and_english():
    idx = BM25Index([chunk("RAG pipeline best practices"), chunk("Spark tuning")])
    assert idx.search("檢索增強")[0].chunk.title == "RAG pipeline best practices"


def test_search_filters():
    idx = BM25Index([
        chunk("Agent 評估 A", date="2026-11-01", priority="skim", tags=["評估"]),
        chunk("Agent 評估 B", date="2026-11-10", priority="must_read", tags=["Agent"]),
    ])
    assert [h.chunk.title for h in idx.search("agent", date_from="2026-11-05")] == ["Agent 評估 B"]
    assert [h.chunk.title for h in idx.search("agent", priority="skim")] == ["Agent 評估 A"]
    assert [h.chunk.title for h in idx.search("agent", tag="評估")] == ["Agent 評估 A"]
    with pytest.raises(ValueError):
        idx.search("agent", priority="urgent")
    with pytest.raises(ValueError):
        idx.search("agent", date_from="11/05")


def test_search_returns_nothing_for_unrelated_query():
    idx = BM25Index([chunk("Spark tuning")])
    assert idx.search("量子力學") == []
    assert idx.search("") == []


# ---------- 評估（回歸門檻：改程式讓檢索變差時，測試會擋下來） ----------

def test_retrieval_quality_regression_gate():
    result = evaluate.run_ablation()[0]
    assert result.hit_at_k >= 0.85, result.misses
    assert result.mrr >= 0.80


def test_eval_set_is_well_formed():
    urls = {c.url for c in load_corpus(evaluate.DEFAULT_CORPUS)}
    for q in evaluate.load_questions():
        assert q["question"] and q["difficulty"] in {"easy", "hard"}
        assert q["relevant"] and all(r["url"] in urls for r in q["relevant"])


# ---------- 生成 ----------

def test_validate_citations_drops_unknown_sources():
    text, dropped = answer.validate_citations("A [S1]，B [S7]，C [S2]", n_sources=2)
    assert text == "A [S1]，B ，C [S2]" and dropped == [7]


class FakeClient:
    def __init__(self, payload, stop_reason="end_turn"):
        self.calls = []
        response = SimpleNamespace(
            stop_reason=stop_reason, stop_details=None, model="claude-test",
            usage=SimpleNamespace(input_tokens=10, output_tokens=5),
            content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text=json.dumps(payload))],
        )

        def create(**kwargs):
            self.calls.append(kwargs)
            return response

        self.beta = SimpleNamespace(messages=SimpleNamespace(create=create))


@pytest.fixture
def small_index():
    return BM25Index([chunk("MCP server 設計模式", summary="把 API 包成 MCP tools"), chunk("Spark tuning")])


def test_answer_without_hits_skips_llm(small_index):
    client = FakeClient({"answer": "不該被呼叫", "insufficient_context": False, "follow_up": []})
    result = answer.answer_question(small_index, "量子力學", client=client)
    assert result.generated_by == "no-hits" and result.insufficient_context and not client.calls


def test_answer_falls_back_to_extractive_without_key(small_index, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    result = answer.answer_question(small_index, "MCP 設計")
    assert result.generated_by == "extractive" and "[S1]" in result.answer


def test_answer_with_claude_validates_citations(small_index):
    client = FakeClient({"answer": "把 API 包成 tools [S1]，另見 [S5]", "insufficient_context": False,
                         "follow_up": ["MCP 和 A2A 差在哪？"]})
    result = answer.answer_question(small_index, "MCP 怎麼設計", client=client)
    assert result.generated_by == "claude:claude-test"
    assert result.dropped_citations == [5] and "[S5]" not in result.answer
    assert [i for i, _ in result.cited_sources()] == [1]
    call = client.calls[0]
    assert "[S1] MCP server 設計模式" in call["messages"][0]["content"]
    assert call["output_config"]["format"]["type"] == "json_schema"
    md = result.to_markdown()
    assert "**來源**" in md and "MCP 和 A2A" in md


def test_answer_refusal_falls_back_to_extractive(small_index):
    client = FakeClient({"answer": "x", "insufficient_context": False, "follow_up": []}, stop_reason="refusal")
    assert answer.answer_question(small_index, "MCP", client=client).generated_by == "extractive"


# ---------- MCP server ----------

def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def mcp_client():
    pytest.importorskip("mcp")
    from mcp import Client
    from airag.mcp_server import build_server
    return lambda: Client(build_server(evaluate.DEFAULT_CORPUS))


def test_mcp_lists_read_only_tools(mcp_client):
    async def go():
        async with mcp_client() as client:
            return (await client.list_tools()).tools

    tools = {t.name: t for t in run(go())}
    assert set(tools) == {"search_notes", "ask_notes", "list_digests", "get_digest"}
    assert all(t.annotations.read_only_hint for t in tools.values())
    assert "query" in tools["search_notes"].input_schema["properties"]


def test_mcp_search_notes_returns_structured_results(mcp_client):
    async def go():
        async with mcp_client() as client:
            return await client.call_tool("search_notes", {"query": "MCP 多租戶", "k": 3})

    result = run(go())
    assert not result.is_error
    data = result.structured_content
    assert data["count"] >= 1 and "MoEngage" in data["results"][0]["title"]


def test_mcp_rejects_bad_input(mcp_client):
    async def go():
        async with mcp_client() as client:
            return [
                await client.call_tool("get_digest", {"date": "../../etc/passwd"}),
                await client.call_tool("get_digest", {"date": "1999-01-01"}),
                await client.call_tool("search_notes", {"query": "rag", "k": 999}),
            ]

    assert all(r.is_error for r in run(go()))


def test_mcp_list_and_get_digest(mcp_client):
    async def go():
        async with mcp_client() as client:
            listing = await client.call_tool("list_digests", {"limit": 2})
            day = await client.call_tool("get_digest", {"date": "2026-11-17"})
            return listing, day

    listing, day = run(go())
    assert not listing.is_error and not day.is_error
    assert "2026-11-17" in day.content[0].text
