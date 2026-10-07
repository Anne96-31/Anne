"""國際與台股市場儀表板。"""
import logging

log = logging.getLogger(__name__)

DASHBOARD = [
    ("台股加權指數", "^TWII"),
    ("櫃買指數", "^TWOII"),
    ("台積電 ADR", "TSM"),
    ("費城半導體", "^SOX"),
    ("那斯達克", "^IXIC"),
    ("標普 500", "^GSPC"),
    ("道瓊工業", "^DJI"),
    ("日經 225", "^N225"),
    ("韓國 KOSPI", "^KS11"),
    ("上證指數", "000001.SS"),
    ("VIX 恐慌指數", "^VIX"),
    ("美國 10 年債殖利率", "^TNX"),
    ("美元指數", "DX-Y.NYB"),
    ("美元/新台幣", "TWD=X"),
    ("WTI 原油", "CL=F"),
    ("黃金", "GC=F"),
]


def load_dashboard():
    import yfinance as yf

    rows = []
    symbols = [s for _, s in DASHBOARD]
    try:
        data = yf.download(symbols, period="1mo", interval="1d", group_by="ticker",
                           auto_adjust=False, progress=False)
    except Exception as e:  # noqa: BLE001
        log.warning("dashboard download failed: %s", e)
        return rows
    for name, sym in DASHBOARD:
        try:
            close = data[sym]["Close"].dropna()
        except KeyError:
            continue
        if len(close) < 6:
            continue
        rows.append({
            "name": name,
            "last": float(close.iloc[-1]),
            "d1": float(close.iloc[-1] / close.iloc[-2] - 1) * 100,
            "d5": float(close.iloc[-1] / close.iloc[-6] - 1) * 100,
            "date": close.index[-1].strftime("%m/%d"),
        })
    return rows
