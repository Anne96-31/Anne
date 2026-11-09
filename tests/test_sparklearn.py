"""sparklearn 的單元測試：不碰網路、不需要任何 secret。"""

import json

import pytest

from sparklearn import __main__ as cli
from sparklearn.markdown import inline, parse


def _text(rich):
    return "".join(r["text"]["content"] for r in rich)


def test_inline_bold_code_and_link():
    rich = inline("用 **Catalyst** 跑 `count()`，見 [文件](https://spark.apache.org)")
    assert _text(rich) == "用 Catalyst 跑 count()，見 文件"
    bold = next(r for r in rich if r["text"]["content"] == "Catalyst")
    code = next(r for r in rich if r["text"]["content"] == "count()")
    link = next(r for r in rich if r["text"]["content"] == "文件")
    assert bold["annotations"]["bold"]
    assert code["annotations"]["code"]
    assert link["text"]["link"]["url"] == "https://spark.apache.org"


def test_inline_code_inside_bold_keeps_both():
    rich = inline("**用 `broadcast` 廣播**")
    code = next(r for r in rich if r["text"]["content"] == "broadcast")
    assert code["annotations"]["bold"] and code["annotations"]["code"]


def test_parse_extracts_title_and_block_types():
    md = """# 第 9 課：測試

> 💡 重點提示

## 小節

段落第一行
段落第二行

- 項目
1. 第一步

| A | B |
|---|---|
| `x` | 2 |

```py
print(1)
```

---

<details>
<summary>參考答案</summary>

```python
x = 1
```

</details>
"""
    title, blocks = parse(md)
    assert title == "第 9 課：測試"
    types = [b["type"] for b in blocks]
    assert types == ["callout", "heading_2", "paragraph", "bulleted_list_item",
                     "numbered_list_item", "table", "code", "divider", "toggle"]

    assert blocks[0]["callout"]["icon"]["emoji"] == "💡"
    assert _text(blocks[0]["callout"]["rich_text"]) == "重點提示"
    assert _text(blocks[2]["paragraph"]["rich_text"]) == "段落第一行 段落第二行"

    table = blocks[5]["table"]
    assert table["table_width"] == 2 and table["has_column_header"]
    assert len(table["children"]) == 2          # 分隔列不算

    assert blocks[6]["code"]["language"] == "python"
    toggle = blocks[8]["toggle"]
    assert _text(toggle["rich_text"]) == "參考答案"
    assert [c["type"] for c in toggle["children"]] == ["code"]


def test_unknown_code_language_falls_back_to_plain_text():
    _, blocks = parse("```text\na → b\n```")
    assert blocks[0]["code"]["language"] == "plain text"


@pytest.mark.parametrize("path", cli.lesson_files(), ids=lambda p: p.name)
def test_every_lesson_converts_within_notion_limits(path):
    title, blocks = cli.build_page(path)
    assert title.startswith(cli.TITLE_PREFIX) and "第" in title
    assert blocks
    assert len(json.dumps(blocks).encode()) < 500_000   # Notion 單次請求上限
    for block in blocks:
        body = block[block["type"]]
        for rich in body.get("rich_text", []):
            assert len(rich["text"]["content"]) <= 2000


def test_lesson_filter():
    assert [p.name[:2] for p in cli.lesson_files([1, 3])] == ["01", "03"]


class FakeNotion:
    """記錄每個請求，並模擬母頁底下已有的子頁。"""

    def __init__(self, children):
        self.children = children          # block_id -> list of blocks
        self.calls = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path.split("?")[0], payload))
        if method == "GET" and path.startswith("/blocks/"):
            return {"results": self.children.get(path.split("/")[2], []), "has_more": False}
        if method == "POST" and path == "/pages":
            return {"id": "new-page", "url": "https://notion.so/new-page"}
        if method == "GET" and path.startswith("/pages/"):
            return {"url": "https://notion.so/old-page"}
        return {}


def test_upsert_creates_new_page_and_appends_overflow():
    fake = FakeNotion({"parent": []})
    blocks = [{"type": "divider", "divider": {}}] * 120
    url = cli.upsert_page(fake, "parent", "Spark & Databricks｜第 1 課", blocks)
    assert url == "https://notion.so/new-page"
    post = next(c for c in fake.calls if c[0] == "POST")
    assert post[2]["parent"]["page_id"] == "parent"
    assert len(post[2]["children"]) == cli.MAX_CHILDREN
    patch = [c for c in fake.calls if c[0] == "PATCH"]
    assert len(patch) == 1 and len(patch[0][2]["children"]) == 120 - cli.MAX_CHILDREN


def test_upsert_rewrites_existing_page_in_place():
    title = "Spark & Databricks｜第 1 課"
    fake = FakeNotion({
        "parent": [{"type": "child_page", "id": "old-page", "child_page": {"title": title}},
                   {"type": "child_page", "id": "other", "child_page": {"title": "別的筆記"}}],
        "old-page": [{"id": "b1"}, {"id": "b2"}],
    })
    url = cli.upsert_page(fake, "parent", title, [{"type": "divider", "divider": {}}])
    assert url == "https://notion.so/old-page"
    assert ("DELETE", "/blocks/b1", None) in fake.calls
    assert ("DELETE", "/blocks/b2", None) in fake.calls
    assert not any(c[0] == "POST" for c in fake.calls)       # 不會重複建頁
    assert not any("other" in c[1] for c in fake.calls)      # 不碰其他筆記
