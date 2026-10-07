"""刪除超過保存天數的日報檔案（reports/YYYY-MM-DD.md、YYYY-MM-DD-picks.csv）。

執行：python -m twdaily.cleanup [reports] [--days 15]
latest.md / latest.json 不受影響。
"""
import argparse
import logging
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from .report import TPE

log = logging.getLogger(__name__)
DATED = re.compile(r"(\d{4}-\d{2}-\d{2})(?:-picks)?\.(md|csv)")
DEFAULT_DAYS = 15


def cutoff_date(days: int, today: date | None = None) -> date:
    """早於此日期（不含）的日報會被刪除，也就是只保留最近 days 天。"""
    today = today or datetime.now(TPE).date()
    return today - timedelta(days=days)


def prune_reports(out_dir: Path, days: int = DEFAULT_DAYS, today: date | None = None):
    cutoff = cutoff_date(days, today)
    removed = []
    for path in sorted(out_dir.glob("*")):
        m = DATED.fullmatch(path.name)
        if m and date.fromisoformat(m.group(1)) < cutoff:
            path.unlink()
            removed.append(path.name)
    log.info("刪除 %d 個超過 %d 天的日報檔案（早於 %s）%s", len(removed), days, cutoff,
             "：" + "、".join(removed) if removed else "")
    return removed


def main():
    parser = argparse.ArgumentParser(description="刪除過期日報")
    parser.add_argument("out", nargs="?", type=Path, default=Path("reports"))
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    prune_reports(args.out, args.days)


if __name__ == "__main__":
    main()
