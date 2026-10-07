from datetime import date

from twdaily import notion
from twdaily.cleanup import cutoff_date, prune_reports


def test_cutoff_keeps_last_15_days():
    assert cutoff_date(15, date(2026, 10, 22)) == date(2026, 10, 7)


def test_prune_reports(tmp_path):
    names = ["2026-10-06.md", "2026-10-06-picks.csv", "2026-10-07.md", "2026-10-07-picks.csv",
             "2026-10-22.md", "latest.md", "latest.json", ".gitkeep", "notes-2026-01-01.md"]
    for n in names:
        (tmp_path / n).write_text("x")
    removed = prune_reports(tmp_path, 15, today=date(2026, 10, 22))
    assert removed == ["2026-10-06-picks.csv", "2026-10-06.md"]
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(set(names) - set(removed))


def test_notion_prune_paginates(monkeypatch):
    pages = {None: (["a", "b"], "cur1"), "cur1": (["c"], None)}
    calls = []

    def fake_call(self, method, path, body=None):
        calls.append((method, path, dict(body) if body else None))
        if path.endswith("/query"):
            ids, nxt = pages[body.get("start_cursor")]
            return {"results": [{"id": i} for i in ids], "has_more": nxt is not None, "next_cursor": nxt}
        return {}

    monkeypatch.setattr(notion.Notion, "call", fake_call)
    assert notion.Notion("tok").prune_before("db", "2026-10-07") == 3
    query = calls[0][2]
    assert query["filter"] == {"property": "日期", "date": {"before": "2026-10-07"}}
    archived = [c[1] for c in calls if c[0] == "PATCH"]
    assert archived == ["/pages/a", "/pages/b", "/pages/c"]
