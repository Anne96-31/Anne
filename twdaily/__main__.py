"""執行：python -m twdaily [--top 800] [--out reports]"""
import argparse
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import data, market, news, report, screener

log = logging.getLogger("twdaily")


def run(top_n: int, out_dir: Path):
    today = datetime.now(report.TPE)
    log.info("載入股票清單…")
    universe = data.load_universe(top_n)
    industries = data.load_industries()
    log.info("下載 %d 檔日線…", len(universe))
    prices = data.load_prices(universe["symbol"].tolist())

    picks, data_dates = [], []
    for row in universe.itertuples():
        df = prices.get(row.symbol)
        if df is None:
            continue
        data_dates.append(df.index[-1])
        res = screener.evaluate(df)
        if res:
            res.update(code=row.code, name=row.name, market=row.market,
                       industry=industries.get(row.code, "—"), value=row.value)
            picks.append(res)
    picks_df = pd.DataFrame(picks)
    if not picks_df.empty:
        picks_df = picks_df.sort_values(["score", "value"], ascending=False).reset_index(drop=True)
    data_date = max(data_dates).strftime("%Y-%m-%d") if data_dates else "N/A"

    log.info("市場儀表板、三大法人、新聞…")
    dashboard = market.load_dashboard()
    institutional = data.load_institutional(data_date.replace("-", "")) if data_dates else None
    headlines = news.load_news()

    md = report.build(today.strftime("%Y-%m-%d"), data_date, dashboard, institutional,
                      picks_df, headlines, scanned=len(prices))
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{today:%Y-%m-%d}.md"
    path.write_text(md, encoding="utf-8")
    (out_dir / "latest.md").write_text(md, encoding="utf-8")
    if not picks_df.empty:
        picks_df.to_csv(out_dir / f"{today:%Y-%m-%d}-picks.csv", index=False, encoding="utf-8-sig")
    log.info("完成：%s（入選 %d 檔）", path, len(picks_df))
    return path


def main():
    parser = argparse.ArgumentParser(description="台股每日投資日報")
    parser.add_argument("--top", type=int, default=800, help="依成交金額掃描前 N 檔（預設 800）")
    parser.add_argument("--out", type=Path, default=Path("reports"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(args.top, args.out)


if __name__ == "__main__":
    main()
