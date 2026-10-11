"""刪除超過保存天數的摘要：digests/YYYY-MM-DD.md 與 Notion 上的舊頁面。

執行：python -m aidigest.cleanup [digests] [--days 30] [--dry-run]
state.json 不受影響（它負責文章去重複，另有自己的保存邏輯）。
"""

from __future__ import annotations

import argparse
import logging
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from . import config, notion

log = logging.getLogger(__name__)
DATED = re.compile(r"(\d{4}-\d{2}-\d{2})\.md")
DEFAULT_DAYS = config.RETENTION_DAYS


def cutoff_date(days: int, today: date | None = None) -> date:
    """早於此日期（不含）的摘要會被刪除，也就是只保留最近 days 天。"""
    today = today or datetime.now(config.TPE).date()
    return today - timedelta(days=days)


def prune_files(out_dir: Path, days: int = DEFAULT_DAYS, today: date | None = None,
                dry_run: bool = False) -> list[str]:
    """清掉 digests/ 裡過期的 Markdown。"""
    cutoff = cutoff_date(days, today)
    removed = []
    for path in sorted(out_dir.glob("*.md")):
        m = DATED.fullmatch(path.name)
        if m and date.fromisoformat(m.group(1)) < cutoff:
            if not dry_run:
                path.unlink()
            removed.append(path.name)
    log.info("檔案清理：%s %d 個超過 %d 天的摘要（早於 %s）%s",
             "將刪除" if dry_run else "已刪除", len(removed), days, cutoff,
             "：" + "、".join(removed) if removed else "")
    return removed


def prune_all(out_dir: Path | None = None, days: int = DEFAULT_DAYS,
              dry_run: bool = False) -> tuple[list[str], list[str]]:
    """同時清 GitHub 上的檔案與 Notion 上的頁面。"""
    out_dir = out_dir or config.OUT_DIR
    today = datetime.now(config.TPE).date()
    files = prune_files(out_dir, days, today, dry_run) if out_dir.exists() else []
    try:
        pages = notion.prune_pages(days, today, dry_run)
    except notion.NotionError as exc:
        # 清理失敗不該讓當天的摘要算成失敗
        log.warning("Notion 清理失敗（不影響當天摘要）：%s", exc)
        pages = []
    return files, pages


def main() -> None:
    parser = argparse.ArgumentParser(description="刪除過期的每日摘要（檔案 + Notion 頁面）")
    parser.add_argument("out", nargs="?", type=Path, default=config.OUT_DIR)
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--dry-run", action="store_true", help="只列出會刪什麼，不實際刪除")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    prune_all(args.out, args.days, args.dry_run)


if __name__ == "__main__":
    main()
