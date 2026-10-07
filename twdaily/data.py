"""資料抓取：上市櫃股票清單、產業別、日線價格、三大法人。"""
import logging
import time

import pandas as pd
import requests

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 (twdaily report bot)"}

TWSE_DAY_ALL = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
TPEX_DAY_ALL = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes"
TWSE_COMPANY = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
TPEX_COMPANY = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"
TWSE_INSTITUTIONAL = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"

INDUSTRY = {
    "01": "水泥", "02": "食品", "03": "塑膠", "04": "紡織纖維", "05": "電機機械",
    "06": "電器電纜", "08": "玻璃陶瓷", "09": "造紙", "10": "鋼鐵", "11": "橡膠",
    "12": "汽車", "14": "建材營造", "15": "航運", "16": "觀光餐旅", "17": "金融保險",
    "18": "貿易百貨", "19": "綜合", "20": "其他", "21": "化學", "22": "生技醫療",
    "23": "油電燃氣", "24": "半導體", "25": "電腦週邊", "26": "光電", "27": "通信網路",
    "28": "電子零組件", "29": "電子通路", "30": "資訊服務", "31": "其他電子",
    "32": "文化創意", "33": "農業科技", "34": "電子商務", "35": "綠能環保",
    "36": "數位雲端", "37": "運動休閒", "38": "居家生活",
}

# 開放資料抓不到時的備援清單（大型權值股與熱門股）
FALLBACK = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2308": "台達電", "2382": "廣達",
    "2412": "中華電", "2881": "富邦金", "2882": "國泰金", "2891": "中信金", "3711": "日月光投控",
    "2303": "聯電", "2886": "兆豐金", "2357": "華碩", "3231": "緯創", "2345": "智邦",
    "6669": "緯穎", "2884": "玉山金", "2892": "第一金", "1216": "統一", "2002": "中鋼",
    "1303": "南亞", "1301": "台塑", "2603": "長榮", "2609": "陽明", "2615": "萬海",
    "3008": "大立光", "2379": "瑞昱", "3034": "聯詠", "2395": "研華", "4938": "和碩",
    "2301": "光寶科", "3017": "奇鋐", "2376": "技嘉", "2356": "英業達", "2327": "國巨",
    "3037": "欣興", "2408": "南亞科", "2344": "華邦電", "3443": "創意", "3661": "世芯-KY",
    "5269": "祥碩", "2207": "和泰車", "1101": "台泥", "2912": "統一超", "5880": "合庫金",
    "2880": "華南金", "2885": "元大金", "2887": "台新金", "2890": "永豐金", "1590": "亞德客-KY",
}


def _get_json(url, params=None, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001 - 公開資料源偶有不穩，重試即可
            log.warning("GET %s failed (%s), retry %d", url, e, i + 1)
            time.sleep(2 ** i)
    return None


def _num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return 0.0


def _pick(row, *keys):
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return None


def load_universe(top_n: int = 800) -> pd.DataFrame:
    """回傳欄位 code, name, market, symbol, value 的股票清單，依當日成交金額取前 top_n 檔。"""
    rows = []
    for item in _get_json(TWSE_DAY_ALL) or []:
        code = str(_pick(item, "Code") or "")
        rows.append({"code": code, "name": _pick(item, "Name"), "market": "上市",
                     "symbol": f"{code}.TW", "value": _num(_pick(item, "TradeValue") or 0)})
    for item in _get_json(TPEX_DAY_ALL) or []:
        code = str(_pick(item, "SecuritiesCompanyCode", "Code") or "")
        rows.append({"code": code, "name": _pick(item, "CompanyName", "Name"), "market": "上櫃",
                     "symbol": f"{code}.TWO",
                     "value": _num(_pick(item, "TransactionAmount", "TradeValue") or 0)})

    df = pd.DataFrame(rows)
    if df.empty:
        log.warning("開放資料無法取得，改用備援清單")
        return pd.DataFrame([{"code": c, "name": n, "market": "上市", "symbol": f"{c}.TW", "value": 0}
                             for c, n in FALLBACK.items()])
    # 只保留一般股票：4 碼數字且非 00 開頭（排除 ETF、權證、特別股）
    df = df[df["code"].str.fullmatch(r"[1-9]\d{3}")]
    return df.sort_values("value", ascending=False).head(top_n).reset_index(drop=True)


def load_industries() -> dict:
    """股票代號 -> 產業別中文名稱。"""
    result = {}
    for url in (TWSE_COMPANY, TPEX_COMPANY):
        for item in _get_json(url) or []:
            code = _pick(item, "公司代號", "SecuritiesCompanyCode")
            ind = _pick(item, "產業別", "SecuritiesIndustryCode")
            if code and ind:
                ind = str(ind).zfill(2)
                result[str(code)] = INDUSTRY.get(ind, ind)
    return result


def load_prices(symbols, period="9mo", chunk=100) -> dict:
    """回傳 symbol -> DataFrame(Close, Volume)。"""
    import yfinance as yf

    out = {}
    for i in range(0, len(symbols), chunk):
        batch = list(symbols[i:i + chunk])
        try:
            data = yf.download(batch, period=period, interval="1d", group_by="ticker",
                               auto_adjust=True, threads=True, progress=False)
        except Exception as e:  # noqa: BLE001
            log.warning("yfinance batch %d failed: %s", i, e)
            continue
        for sym in batch:
            try:
                sub = data[sym] if isinstance(data.columns, pd.MultiIndex) else data
                sub = sub[["Close", "Volume"]].dropna(subset=["Close"])
                if not sub.empty:
                    out[sym] = sub
            except KeyError:
                continue
        time.sleep(1)
    return out


def load_institutional(date_str: str):
    """三大法人買賣金額（上市）。date_str: YYYYMMDD。回傳 list[dict] 或 None。"""
    data = _get_json(TWSE_INSTITUTIONAL, {"response": "json", "dayDate": date_str, "type": "day"})
    if not data or data.get("stat") != "OK":
        return None
    rows = []
    for r in data.get("data", []):
        rows.append({"name": r[0], "buy": _num(r[1]) / 1e8, "sell": _num(r[2]) / 1e8,
                     "net": _num(r[3]) / 1e8})
    return rows
