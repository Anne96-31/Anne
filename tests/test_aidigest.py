"""aidigest 的單元測試：全部不碰網路、不需要任何 secret。"""

from datetime import date, datetime, timedelta, timezone

import pytest

from aidigest import cleanup, fetch, notion, ranking, render, summarize
from aidigest import sources as src


# ---------- 來源清單 ----------

def test_sources_have_required_fields():
    for source in src.SOURCES:
        assert source["key"] and source["name"] and source["url"]
        assert source["category"] in src.CATEGORY_LABELS
        assert source["type"] in {"rss", "manual"}


def test_source_keys_are_unique():
    keys = [s["key"] for s in src.SOURCES]
    assert len(keys) == len(set(keys))


def test_core_sources_include_requested_sites():
    core = {s["key"] for s in src.SOURCES if s["category"] == "core"}
    assert {"kdnuggets", "tds", "analyticsvidhya", "techorange", "uber_eng"} <= core


# ---------- Notion ID 解析 ----------

@pytest.mark.parametrize("raw, expected", [
    ("3d004eec343480308dece80fae274209", "3d004eec-3434-8030-8dec-e80fae274209"),
    ("3d004eec-3434-8030-8dec-e80fae274209", "3d004eec-3434-8030-8dec-e80fae274209"),
    # 標題裡的 a-f 字母（AI-Data-）不可以被當成 ID 的一部分
    ("https://app.notion.com/p/AI-Data-3d004eec343480308dece80fae274209",
     "3d004eec-3434-8030-8dec-e80fae274209"),
    ("https://www.notion.so/My-Page-3d004eec343480308dece80fae274209?pvs=4",
     "3d004eec-3434-8030-8dec-e80fae274209"),
])
def test_normalize_id(raw, expected):
    assert notion.normalize_id(raw) == expected


def test_normalize_id_rejects_garbage():
    with pytest.raises(notion.NotionError):
        notion.normalize_id("not-a-notion-page")


# ---------- 只清理自己產生的頁面 ----------

@pytest.mark.parametrize("title, expected", [
    ("AI & Data 每日摘要 2026-09-14（一）", date(2026, 9, 14)),
    ("AI & Data 每日摘要 2026-10-11", date(2026, 10, 11)),
    ("我的其他筆記", None),                      # 別人的頁面：絕對不能動
    ("AI & Data 每日摘要（沒有日期）", None),
    ("Random 2026-01-01", None),
    ("AI & Data 每日摘要 2026-13-45", None),     # 不合法日期
])
def test_digest_page_date(title, expected):
    assert notion.digest_page_date(title) == expected


# ---------- 保存天數 ----------

def test_cutoff_date_keeps_last_n_days():
    today = date(2026, 10, 11)
    assert cleanup.cutoff_date(30, today) == date(2026, 9, 11)


def test_prune_files_only_removes_expired(tmp_path):
    today = date(2026, 10, 11)
    for name in ["2026-10-11.md", "2026-09-12.md", "2026-09-11.md",
                 "2026-09-10.md", "2026-08-01.md", "latest.md", "state.json"]:
        (tmp_path / name).write_text("x", encoding="utf-8")

    removed = cleanup.prune_files(tmp_path, days=30, today=today)

    assert sorted(removed) == ["2026-08-01.md", "2026-09-10.md"]
    assert (tmp_path / "latest.md").exists()      # latest 與 state 不受影響
    assert (tmp_path / "state.json").exists()
    assert (tmp_path / "2026-09-11.md").exists()  # 剛好在保留邊界上


def test_prune_files_dry_run_keeps_everything(tmp_path):
    (tmp_path / "2026-01-01.md").write_text("x", encoding="utf-8")
    removed = cleanup.prune_files(tmp_path, days=30, today=date(2026, 10, 11), dry_run=True)
    assert removed == ["2026-01-01.md"]
    assert (tmp_path / "2026-01-01.md").exists()


# ---------- feed 解析 ----------

def test_entry_datetime_survives_out_of_range_timestamp():
    """實際踩過：某些 feed 的壞日期會讓 datetime.fromtimestamp 在 Windows 丟 OSError。"""
    bad = {"published_parsed": (12026, 1, 1, 0, 0, 0, 0, 1, 0)}
    assert fetch.entry_datetime(bad).year > 2000

    nonsense = {"published_parsed": (1, 1, 1, 0, 0, 0, 0, 1, 0)}
    fetch.entry_datetime(nonsense)        # 不能拋例外


def test_entry_datetime_defaults_to_now():
    before = datetime.now(timezone.utc)
    got = fetch.entry_datetime({})
    assert got >= before - timedelta(seconds=5)


def test_clean_text_strips_html_and_entities():
    # &nbsp; 解碼後是不換行空白，會被 \s+ 一併收斂成普通空白，這是刻意的
    assert fetch.clean_text("<p>Hello&nbsp;<b>World</b></p>") == "Hello World"
    assert fetch.clean_text("<script>bad()</script>ok") == "ok"
    assert fetch.clean_text("") == ""


def test_clean_text_respects_limit():
    assert len(fetch.clean_text("a" * 5000, limit=100)) == 100


# ---------- 排序 ----------

def make_article(title, summary="", *, source_key="tds", name="Towards Data Science",
                 category="core", weight=3.0, age_hours=2.0):
    return fetch.Article(
        title=title,
        link=f"https://example.com/{abs(hash(title))}",
        published=datetime.now(timezone.utc) - timedelta(hours=age_hours),
        summary=summary,
        source_key=source_key,
        source_name=name,
        category=category,
        source_weight=weight,
    )


def test_data_engineering_plus_ai_gets_bridge_bonus():
    """同時談資料管線與 RAG 的文章，要贏過只談其中一邊的。"""
    bridge = ranking.score_article(make_article(
        "Building a RAG pipeline on Spark", "embedding pipeline with airflow and vector search"))
    only_de = ranking.score_article(make_article(
        "Building a Spark pipeline", "airflow orchestration for a data warehouse"))
    assert bridge.score > only_de.score
    assert "data_platform" in bridge.themes and "llm_app" in bridge.themes


def test_chinese_keywords_are_matched():
    """TechOrange 是中文媒體，中文關鍵字必須能命中主題。"""
    art = ranking.score_article(make_article(
        "企業如何導入生成式 AI：從資料管線到推論部署",
        "本文談架構與落地案例", source_key="techorange", name="TechOrange 科技報橘"))
    assert art.themes, "中文標題應該要被分類到主題"
    assert art.score > art.source_weight


def test_business_noise_is_penalised():
    noisy = ranking.score_article(make_article("OpenAI raises $10B in funding round"))
    plain = ranking.score_article(make_article("OpenAI releases a new model"))
    assert noisy.score < plain.score


def test_rank_respects_per_source_cap():
    arts = [make_article(f"RAG agent evaluation {i}") for i in range(10)]
    picked = ranking.rank(arts, max_items=10, max_per_source=3)
    assert len([a for a in picked if a.source_key == "tds"]) <= 3


def test_rank_caps_research_flood():
    """arXiv 一天上百篇，不能把整份摘要洗掉。"""
    papers = [make_article(f"RAG agent paper {i}", "agentic retrieval pipeline evaluation",
                           source_key="arxiv_lg", name="arXiv", category="research", weight=0.6)
              for i in range(20)]
    others = [make_article(f"Practical guide {i}", "how to build an agent in production")
              for i in range(5)]
    picked = ranking.rank(papers + others, max_items=10, max_per_source=4)
    assert len([a for a in picked if a.category == "research"]) <= 1


def test_fresher_article_scores_higher():
    fresh = ranking.score_article(make_article("RAG in production", age_hours=1))
    stale = ranking.score_article(make_article("RAG in production", age_hours=200))
    assert fresh.score > stale.score


# ---------- 摘要與輸出 ----------

def test_offline_summary_covers_every_article():
    arts = [ranking.score_article(make_article(f"Agent eval {i}")) for i in range(3)]
    result = summarize.offline_summary(arts)
    assert [i["index"] for i in result["items"]] == [1, 2, 3]
    assert result["briefing"] and len(result["learning_plan"]) == 3
    for item in result["items"]:
        assert item["priority"] in summarize.PRIORITY_LABEL


def test_summarize_without_llm_never_calls_api():
    arts = [ranking.score_article(make_article("RAG pipeline"))]
    result, by_llm = summarize.summarize(arts, use_llm=False)
    assert by_llm is False and len(result["items"]) == 1


def test_result_schema_requires_all_item_fields():
    item = summarize.RESULT_SCHEMA["properties"]["items"]["items"]
    assert set(item["required"]) == set(item["properties"])
    assert item["additionalProperties"] is False


def test_build_markdown_contains_links_and_sections():
    arts = [ranking.score_article(make_article("RAG pipeline on Spark", "embedding airflow"))]
    result = summarize.offline_summary(arts)
    md = render.build_markdown(arts, result, generated_by="測試", scanned=1,
                               now=datetime.now(), title="測試摘要")
    assert "# 測試摘要" in md
    assert arts[0].link in md
    assert "對你的意義" in md


def test_build_blocks_are_valid_notion_payloads():
    arts = [ranking.score_article(make_article("RAG pipeline on Spark", "embedding airflow"))]
    result = summarize.offline_summary(arts)
    blocks = render.build_blocks(arts, result, generated_by="測試", scanned=1,
                                 now=datetime.now())
    assert blocks

    def walk(items, depth=0):
        assert depth <= 2, "Notion 建立頁面時最多兩層巢狀"
        for block in items:
            kind = block["type"]
            body = block[kind]
            for rt in body.get("rich_text", []):
                assert rt["type"] == "text"
                assert len(rt["text"]["content"]) <= 2000
            walk(body.get("children", []), depth + 1)

    walk(blocks)
