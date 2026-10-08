from datetime import date
from types import SimpleNamespace

from dailyenglish import __main__ as app
from dailyenglish.lesson import Lesson, generate, to_markdown
from twdaily import notion


def sample_lesson():
    return Lesson(
        theme="Semiconductors & AI",
        goals_zh=["掌握 10 個詞彙", "讀懂產業分析", "練習委婉語氣"],
        vocabulary=[{"word": f"word{i}", "part_of_speech": "v.", "meaning_zh": "意思",
                     "collocations": "a | b", "example": f"We **word{i}** it."} for i in range(10)],
        usage_tips_zh=["提醒一"],
        article_title="The Hidden Bottleneck",
        article_paragraphs=["Para one.", "Para two."],
        source_headline="Chip demand surges",
        source_link="https://news.example.com/a",
        comprehension_questions=["Why?", "How?"],
        key_expressions=[{"phrase": "through the lens of", "meaning_zh": "從……角度"}],
        grammar_title="Hedging",
        grammar_explanation_zh="說明",
        grammar_examples=[{"too_direct": "This will fail.", "professional": "This may struggle."}],
        grammar_toolkit="may, might",
        writing_scenario_zh="寫 email 給主管",
        writing_requirements_zh=["100–150 字"],
    )


def test_markdown_renders_to_notion_blocks():
    md = to_markdown(sample_lesson(), 3, date(2026, 10, 8))
    assert "Day 3" in md and "a / b" in md  # 表格內的 | 會被替換
    blocks = notion.markdown_to_blocks(md)
    types = [b["type"] for b in blocks]
    assert types.count("table") == 2
    assert types.count("to_do") == 7
    vocab = next(b for b in blocks if b["type"] == "table")["table"]
    assert vocab["table_width"] == 6 and len(vocab["children"]) == 11


def test_generate_uses_structured_output():
    captured = {}

    class FakeMessages:
        def parse(self, **kw):
            captured.update(kw)
            return SimpleNamespace(stop_reason="end_turn", parsed_output=sample_lesson())

    client = SimpleNamespace(beta=SimpleNamespace(messages=FakeMessages()))
    lesson = generate(date(2026, 10, 8), [{"title": "Chip demand surges", "link": "https://x"}],
                      ["leverage"], ["Hedging"], client=client)
    assert lesson.theme == "Semiconductors & AI"
    assert captured["output_format"] is Lesson
    prompt = captured["messages"][0]["content"]
    assert "leverage" in prompt and "Hedging" in prompt and "Chip demand surges" in prompt


def _page(words, grammar):
    return {"properties": {"詞彙": {"rich_text": [{"plain_text": words}]},
                           "文法重點": {"rich_text": [{"plain_text": grammar}]}}}


def test_history_and_publish(monkeypatch):
    calls = []

    def fake_call(self, method, path, body=None):
        calls.append((method, path, body))
        if path.endswith("/query") and body["filter"]["date"].get("before"):
            if "start_cursor" not in body:
                return {"results": [_page("leverage, mitigate", "Hedging")], "has_more": True, "next_cursor": "c"}
            return {"results": [_page("scrutiny", "Articles")], "has_more": False}
        if path.endswith("/query"):
            return {"results": []}
        if method == "GET":
            return {"properties": {"Name": {"type": "title"}}}
        if path == "/pages":
            return {"id": "new", "url": "https://notion.so/new"}
        return {}

    monkeypatch.setattr(notion.Notion, "call", fake_call)
    client = notion.Notion("tok")
    words, grammar, done = app.load_history(client, "db", "2026-10-08")
    assert words == ["leverage", "mitigate", "scrutiny"]
    assert grammar == ["Hedging", "Articles"] and done == 2

    lesson = sample_lesson()
    app.publish(client, "db", lesson, to_markdown(lesson, 3, date(2026, 10, 8)), 3, "2026-10-08")
    schema = next(c for c in calls if c[0] == "PATCH" and c[1] == "/databases/db")
    assert set(schema[2]["properties"]) == set(app.PROPERTIES)
    page = next(c for c in calls if c[1] == "/pages")[2]
    props = page["properties"]
    assert props["Day"] == {"number": 3}
    assert props["詞彙"]["rich_text"][0]["text"]["content"].startswith("word0, word1")
    assert props["Name"]["title"][0]["text"]["content"].startswith("Day 3｜2026-10-08")
