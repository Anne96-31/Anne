"""每日 AI & Data 產業摘要 → Notion。

執行：
  python -m aidigest                  # 完整流程：抓取 → Claude 摘要 → 寫入 Notion → 存 Markdown
  python -m aidigest --dry-run        # 不寫 Notion，只產生 digests/ 的 Markdown
  python -m aidigest --no-llm         # 不呼叫 Claude，用規則式摘要
  python -m aidigest --check          # 檢查所有來源與 Notion 連線
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime, timedelta

from . import cleanup, config, fetch, notion, ranking, render, summarize
from . import sources as src

WEEKDAYS = "一二三四五六日"
SEEN_RETENTION_DAYS = 60


# ---------- 已推播文章的去重複狀態（存在 digests/state.json，由 workflow commit 回 repo）----------

def load_state() -> dict[str, str]:
    if not config.STATE_FILE.exists():
        return {}
    try:
        return json.loads(config.STATE_FILE.read_text(encoding="utf-8")).get("seen", {})
    except (json.JSONDecodeError, OSError) as exc:
        logging.getLogger("digest").warning("state.json 讀取失敗，重新建立：%s", exc)
        return {}


def save_state(seen: dict[str, str]) -> None:
    cutoff = datetime.now(config.TPE).date() - timedelta(days=SEEN_RETENTION_DAYS)
    kept = {}
    for link, iso in seen.items():
        try:
            if date.fromisoformat(iso) >= cutoff:
                kept[link] = iso
        except ValueError:
            continue
    config.OUT_DIR.mkdir(parents=True, exist_ok=True)
    config.STATE_FILE.write_text(
        json.dumps({"updated": datetime.now(config.TPE).isoformat(timespec="seconds"),
                    "seen": kept}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def check() -> int:
    log = logging.getLogger("check")
    ok = 0
    for source in src.active_sources():
        try:
            ok += 1 if fetch.fetch_source(source) else 0
        except Exception as exc:
            log.warning("抓取失敗 %-24s %s", source["name"], exc)
    log.info("來源檢查：%d / %d 正常", ok, len(src.active_sources()))

    if not config.NOTION_TOKEN:
        log.error("未設定 NOTION_TOKEN")
        return 1
    try:
        log.info("Notion 連線正常，integration = %s", notion.Notion().whoami())
        log.info("寫入目標 ID = %s", notion.normalize_id(config.NOTION_PAGE_ID))
    except notion.NotionError as exc:
        log.error("Notion 檢查失敗：%s", exc)
        return 1

    log.info("Claude：%s", "已設定 API key" if config.ANTHROPIC_API_KEY else "未設定（會用規則式摘要）")
    return 0


def run(args: argparse.Namespace) -> int:
    log = logging.getLogger("digest")
    now = datetime.now(config.TPE)

    log.info("開始抓取（最近 %d 天，共 %d 個 RSS 來源）", args.days, len(src.active_sources()))
    articles = fetch.fetch_all(src.active_sources(), args.days)
    scanned = len(articles)
    log.info("時間範圍內共 %d 篇", scanned)
    if not articles:
        log.error("沒有抓到任何文章，結束。")
        return 1

    seen = load_state()
    if not args.include_seen:
        before = len(articles)
        articles = [a for a in articles if a.dedup_key not in seen]
        log.info("過濾掉 %d 篇先前已推播過的文章", before - len(articles))

    picked = ranking.rank(articles, args.limit, config.MAX_PER_SOURCE)
    if not picked:
        log.error("過濾後沒有可用文章（可試 --include-seen 或加大 --days）。")
        return 1
    log.info("選出 %d 篇，最高分 %.2f", len(picked), picked[0].score)

    result, by_llm = summarize.summarize(picked, use_llm=not args.no_llm)
    engine = f"Claude（{config.ANTHROPIC_MODEL}）" if by_llm else "規則式"
    log.info("摘要完成，引擎：%s", engine)

    title = f"AI & Data 每日摘要 {now:%Y-%m-%d}（{WEEKDAYS[now.weekday()]}）"
    markdown = render.build_markdown(picked, result, generated_by=engine,
                                     scanned=scanned, now=now, title=title)
    config.OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = config.OUT_DIR / f"{now:%Y-%m-%d}.md"
    md_path.write_text(markdown, encoding="utf-8")
    (config.OUT_DIR / "latest.md").write_text(markdown, encoding="utf-8")
    log.info("Markdown 已存到 %s", md_path)

    if args.dry_run:
        log.info("--dry-run：跳過 Notion 寫入。")
    elif not config.NOTION_TOKEN:
        log.warning("未設定 NOTION_TOKEN，跳過 Notion 寫入（Markdown 已保留）。")
    else:
        blocks = render.build_blocks(picked, result, generated_by=engine,
                                     scanned=scanned, now=now)
        try:
            log.info("已寫入 Notion：%s", notion.publish(title, blocks))
        except notion.NotionError as exc:
            log.error("寫入 Notion 失敗：%s", exc)
            return 2

    today_iso = now.date().isoformat()
    for art in picked:
        seen[art.dedup_key] = today_iso
    save_state(seen)

    if args.cleanup_days != 0:
        cleanup.prune_all(config.OUT_DIR, args.cleanup_days, dry_run=args.dry_run)

    log.info("完成。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="每日 AI / Data 產業摘要 → Notion")
    parser.add_argument("--days", type=int, default=config.LOOKBACK_DAYS, help="回看幾天內的文章")
    parser.add_argument("--limit", type=int, default=config.MAX_ITEMS, help="最多收錄幾篇")
    parser.add_argument("--dry-run", action="store_true", help="不寫入 Notion、不實際刪除")
    parser.add_argument("--no-llm", action="store_true", help="不呼叫 Claude，用規則式摘要")
    parser.add_argument("--include-seen", action="store_true", help="不過濾先前推播過的文章")
    parser.add_argument("--check", action="store_true", help="檢查來源與 Notion 連線")
    parser.add_argument("--cleanup-days", type=int, default=config.RETENTION_DAYS, metavar="天",
                        help=f"超過幾天的舊摘要要清掉（預設 {config.RETENTION_DAYS}，0 = 不清理）")
    args = parser.parse_args()

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        return check() if args.check else run(args)
    except KeyboardInterrupt:
        logging.getLogger("digest").warning("使用者中斷。")
        return 130
    except Exception:
        logging.getLogger("digest").exception("未預期的錯誤")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
