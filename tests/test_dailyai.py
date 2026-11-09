from datetime import date
from types import SimpleNamespace

from dailyai import __main__ as app
from dailyai.brief import Brief, generate, to_markdown
from twdaily import notion

HEADLINES = [
    {"title": "Anthropic releases new model", "link": "https://news.example.com/a", "source": "Reuters"},
    {"title": "TSMC expands AI packaging", "link": "https://news.example.com/b", "source": "經濟日報"},
]


def _item(category, title, link):
    return {"category": category, "title_zh": title, "summary_zh": "摘要。", "why_it_matters_zh": "影響。",
            "source_title": "原文", "source_link": link, "source_name": "Reuters"}


def sample_brief(fake_link=False):
    return Brief(
        headline_zh="新模型發布帶動 AI 競賽",
        takeaways_zh=["重點一", "重點二", "重點三"],
        items=[
            _item("🖥️ 晶片與算力", "台積電擴充先進封裝", "https://news.example.com/b"),
            _item("🚀 模型與產品", "Anthropic 推出新模型", "https://news.example.com/a"),
            *([_item("💰 產業與投資", "捏造的新聞", "https://fake.example.com")] if fake_link else []),
        ],
        watch_list_zh=["觀察一", "觀察二"],
        term={"term": "RAG", "explanation_zh": "檢索增強生成。"},
        tags=["Anthropic", "TSMC", "CoWoS"],
    )


def test_markdown_groups_by_category_in_order():
    md = to_markdown(sample_brief(), date(2026, 10, 8))
    assert md.index("# 🚀 模型與產品") < md.index("# 🖥️ 晶片與算力")
    assert "共 2 則" in md and "AI 術語小教室：RAG" in md
    blocks = notion.markdown_to_blocks(md)
    types = [b["type"] for b in blocks]
    assert types.count("quote") == 2
    link = next(b for b in blocks if b["type"] == "bulleted_list_item"
                and "來源" in b["bulleted_list_item"]["rich_text"][0]["text"]["content"])
    assert link["bulleted_list_item"]["rich_text"][1]["text"]["link"]["url"].startswith("https://news.example.com")


def test_generate_drops_items_with_unknown_links():
    captured = {}

    class FakeMessages:
        def parse(self, **kw):
            captured.update(kw)
            return SimpleNamespace(stop_reason="end_turn", parsed_output=sample_brief(fake_link=True))

    client = SimpleNamespace(beta=SimpleNamespace(messages=FakeMessages()))
    brief = generate(date(2026, 10, 8), HEADLINES, ["舊新聞"], ["MoE"], client=client)
    assert [i.title_zh for i in brief.items] == ["台積電擴充先進封裝", "Anthropic 推出新模型"]
    assert captured["output_format"] is Brief
    prompt = captured["messages"][0]["content"]
    assert "舊新聞" in prompt and "MoE" in prompt and "TSMC expands AI packaging" in prompt


def _page(titles, term):
    return {"properties": {"新聞標題": {"rich_text": [{"plain_text": titles}]},
                           "術語": {"rich_text": [{"plain_text": term}]}}}


def test_history_and_publish(monkeypatch):
    calls = []

    def fake_call(self, method, path, body=None):
        calls.append((method, path, body))
        if path.endswith("/query") and body["filter"]["date"].get("before"):
            return {"results": [_page("甲；乙", "RAG"), _page("丙", "MoE"), _page("丁", ""), _page("戊", "LoRA")]}
        if path.endswith("/query"):
            return {"results": []}
        if method == "GET":
            return {"properties": {"Name": {"type": "title"}}}
        if path == "/pages":
            return {"id": "new", "url": "https://notion.so/new"}
        return {}

    monkeypatch.setattr(notion.Notion, "call", fake_call)
    client = notion.Notion("tok")
    titles, terms = app.load_history(client, "db", "2026-10-08")
    assert titles == ["甲", "乙", "丙", "丁"]
    assert terms == ["RAG", "MoE", "LoRA"]

    brief = sample_brief()
    app.publish(client, "db", brief, to_markdown(brief, date(2026, 10, 8)), "2026-10-08")
    schema = next(c for c in calls if c[0] == "PATCH" and c[1] == "/databases/db")
    assert set(schema[2]["properties"]) == set(app.PROPERTIES)
    props = next(c for c in calls if c[1] == "/pages")[2]["properties"]
    assert props["Name"]["title"][0]["text"]["content"] == "2026-10-08｜新模型發布帶動 AI 競賽"
    assert props["則數"] == {"number": 2}
    assert props["新聞標題"]["rich_text"][0]["text"]["content"] == "台積電擴充先進封裝；Anthropic 推出新模型"
    assert [t["name"] for t in props["標籤"]["multi_select"]] == ["Anthropic", "TSMC", "CoWoS"]
