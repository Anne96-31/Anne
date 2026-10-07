# Anne — 台股每日投資日報 📈

每個交易日收盤後自動產生一份日報，內容包含：

1. **市場儀表板**：加權指數、櫃買、台積電 ADR、費半、美股三大指數、日韓陸股、VIX、美債殖利率、美元指數、新台幣匯率、原油、黃金
2. **三大法人買賣超**（上市）
3. **🎯 從低檔翻揚・MACD 轉正個股**：掃描成交金額前 800 名的上市櫃股票
4. **📰 每日必看新聞**：台股盤勢、半導體/AI 產業、傳產金融航運、國際財經（Fed、美股、匯率、地緣政治）
5. **盤後檢查清單**：給新手的每日學習功課

👉 **最新日報：[`reports/latest.md`](reports/latest.md)**，歷史日報都在 [`reports/`](reports/)，入選股另存 CSV（可用 Excel 開啟）。

## 選股邏輯

MACD 參數 12 / 26 / 9，命名依台灣看盤軟體慣例：DIF（快慢線差）、DEM/MACD（訊號線）、OSC（柱狀體）。

| 訊號 | 條件 |
|---|---|
| **低檔金叉** | 近 3 日內 OSC 由負翻正（DIF 上穿 DEM），交叉時 DIF 在零軸下方，且收盤價位於近 120 日區間下半部 |
| **DIF翻正** | 近 3 日內 DIF 由負轉正站上零軸，且先前 20 日中至少 10 日 DIF 為負 |
| 共同過濾 | 最新 OSC 仍為正、近 20 日平均成交金額 ≥ 3,000 萬元 |

**評分（0–7）** = 訊號數 × 2 + 站上月線 + 量比 ≥ 1.5 + RSI 介於 40–65 + OSC 連續放大。

參數集中在 [`twdaily/screener.py`](twdaily/screener.py) 的 `ScreenConfig`，可依個人風格調整。

## 自動排程

[`.github/workflows/daily-report.yml`](.github/workflows/daily-report.yml) 於 **台北時間週一至週五 16:47** 執行，完成後把日報 commit 回 repo。

- 排程只在 **預設分支（master）** 上生效，請先把這個分支合併進 master。
- 也可在 GitHub → Actions → 「台股每日投資日報」→ **Run workflow** 手動執行。

## 本機執行

```bash
pip install -r requirements.txt
python -m twdaily            # 產生 reports/YYYY-MM-DD.md 與 reports/latest.md
python -m twdaily --top 300  # 只掃描成交金額前 300 名（較快）
python -m pytest -q tests
```

## 資料來源

- 股票清單與產業別：臺灣證券交易所、證券櫃檯買賣中心 OpenAPI
- 日線價格與國際指數：Yahoo Finance（`yfinance`）
- 三大法人：臺灣證券交易所
- 新聞：Google News、Yahoo 股市 RSS

> ⚠️ 本專案僅供學習研究，不構成投資建議。技術指標具落後性，請搭配基本面、籌碼面與風險控管。
