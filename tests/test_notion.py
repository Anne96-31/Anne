import json

from twdaily import notion


def test_inline_formatting():
    rt = notion.rich_text("前 **粗體** 與 [連結](https://a.b) 及 `碼`")
    assert [r["text"]["content"] for r in rt] == ["前 ", "粗體", " 與 ", "連結", " 及 ", "碼"]
    assert rt[1]["annotations"] == {"bold": True}
    assert rt[3]["text"]["link"] == {"url": "https://a.b"}
    assert rt[5]["annotations"] == {"code": True}


def test_long_text_split():
    rt = notion.rich_text("字" * 4500)
    assert [len(r["text"]["content"]) for r in rt] == [2000, 2000, 500]


def test_markdown_blocks():
    md = "\n".join([
        "# 標題", "", "## 小節", "> 提醒", "- 項目", "- [ ] 待辦", "1. 第一",
        "| A | B |", "|---|---:|", "| 1 | **2** |", "", "_無資料_", "一般段落",
    ])
    blocks = notion.markdown_to_blocks(md)
    assert [b["type"] for b in blocks] == [
        "heading_1", "heading_2", "quote", "bulleted_list_item", "to_do",
        "numbered_list_item", "table", "paragraph", "paragraph",
    ]
    table = blocks[6]["table"]
    assert table["table_width"] == 2 and len(table["children"]) == 2
    assert table["children"][1]["table_row"]["cells"][1][0]["annotations"] == {"bold": True}
    assert blocks[7]["paragraph"]["rich_text"][0]["annotations"] == {"italic": True}


def test_publish_flow(tmp_path, monkeypatch):
    md = tmp_path / "r.md"
    md.write_text("\n".join(f"- 第 {i} 行" for i in range(150)), encoding="utf-8")
    summary = tmp_path / "s.json"
    summary.write_text(json.dumps({"report_date": "2026-10-07", "picks": 3, "twii": 23000.5,
                                   "twii_d1": 1.2, "foreign_net": 50.0,
                                   "top_picks": ["2330 台積電（5分）"], "industries": ["半導體"]}),
                       encoding="utf-8")
    calls = []

    def fake_call(self, method, path, body=None):
        calls.append((method, path, body))
        if path.startswith("/databases/") and method == "GET":
            return {"properties": {"Name": {"type": "title"}, "日期": {"type": "date"}}}
        if path.endswith("/query"):
            return {"results": [{"id": "old"}]}
        if path == "/pages":
            return {"id": "new", "url": "https://notion.so/new"}
        return {}

    monkeypatch.setattr(notion.Notion, "call", fake_call)
    notion.publish(md, summary, "tok", "db", "https://github.com/x")

    patch_schema = calls[1]
    assert patch_schema[0] == "PATCH" and "日期" not in patch_schema[2]["properties"]
    assert ("PATCH", "/pages/old", {"archived": True}) in calls
    create = next(c for c in calls if c[1] == "/pages")[2]
    assert create["properties"]["Name"]["title"][0]["text"]["content"] == "2026-10-07 台股日報｜入選 3 檔"
    assert create["properties"]["報告連結"] == {"url": "https://github.com/x"}
    assert len(create["children"]) == 100
    append = calls[-1]
    assert append[1] == "/blocks/new/children" and len(append[2]["children"]) == 50
