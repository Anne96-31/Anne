# Anne — 台股每日投資日報 📈

每天早上 8:00 自動產生一份日報，內容包含：

1. **市場儀表板**：加權指數、櫃買、台積電 ADR、費半、美股三大指數、日韓陸股、VIX、美債殖利率、美元指數、新台幣匯率、原油、黃金
2. **三大法人買賣超**（上市）
3. **🎯 從低檔翻揚・MACD 轉正個股**：掃描成交金額前 800 名的上市櫃股票
4. **📰 每日必看新聞**：台股盤勢、半導體/AI 產業、傳產金融航運、國際財經（Fed、美股、匯率、地緣政治）
5. **盤後檢查清單**：給新手的每日學習功課

👉 **最新日報：[`reports/latest.md`](reports/latest.md)**，歷史日報都在 [`reports/`](reports/)，入選股另存 CSV（可用 Excel 開啟）。

🗺️ 系統架構圖與各環節程式碼：[`docs/architecture.html`](docs/architecture.html)

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

[`.github/workflows/daily-report.yml`](.github/workflows/daily-report.yml) 於 **每天台北時間 07:43** 開始執行，約 8:00 前完成（涵蓋前一交易日收盤與美股隔夜行情），完成後把日報 commit 回 repo。

- 刻意避開整點：GitHub 免費排程在整點最擁擠，可能延遲數分鐘到數小時。若某天沒準時出現，可到 Actions 手動 **Run workflow**。
- **自動清理**：只保留最近 **15 天** 的日報。過期的 `reports/YYYY-MM-DD.md`、`-picks.csv` 會被刪除（仍可在 git 歷史找回），Notion 中過期的頁面會移到垃圾桶（30 天內可復原）。天數可改 workflow 裡的 `RETENTION_DAYS`。

- 排程只在 **預設分支（master）** 上生效，請先把這個分支合併進 master。
- 也可在 GitHub → Actions → 「台股每日投資日報」→ **Run workflow** 手動執行。

## 同步到 Notion

每天的日報會在 Notion 資料庫新增一頁：完整內容（表格、新聞連結、檢查清單）放在頁面裡，重點數字放在資料庫欄位，可以排序、篩選、做成看板或日曆。

自動建立的欄位：`日期`、`入選檔數`、`加權指數`、`加權漲跌%`、`外資買賣超(億)`、`前五名`、`集中產業`、`報告連結`。同一天重跑會封存舊頁面，不會重複。

**設定步驟（只需做一次）：**

1. **建立 Integration**：打開 <https://www.notion.so/profile/integrations> → **New integration** → 名稱填「台股日報」→ 選你的 Workspace → 類型 Internal → 儲存後複製 **Internal Integration Secret**（`ntn_` 開頭）。
2. **建立資料庫**：在 Notion 新增一個頁面，輸入 `/database` 選 **Database - Full page**，命名為「台股每日日報」。欄位不用自己加，程式會自動補上。
3. **授權資料庫**：在資料庫頁面右上角 **⋯** → **Connections**（連結）→ 搜尋並加入「台股日報」。
4. **取得資料庫 ID**：右上角 **Share** → **Copy link**。網址 `notion.so/` 後面、`?v=` 前面那串 32 碼英數字就是 ID（直接貼整段網址也可以）。
5. **設定 GitHub Secrets**：repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，新增兩個：
   - `NOTION_TOKEN`：第 1 步的 Secret
   - `NOTION_DATABASE_ID`：第 4 步的 ID 或網址
6. 到 **Actions** → 「台股每日投資日報」→ **Run workflow** 測試，完成後 Notion 會出現第一頁。

## 本機執行

```bash
pip install -r requirements.txt
python -m twdaily            # 產生 reports/YYYY-MM-DD.md 與 reports/latest.md
python -m twdaily --top 300  # 只掃描成交金額前 300 名（較快）
python -m pytest -q tests

# 手動同步到 Notion
NOTION_TOKEN=ntn_xxx NOTION_DATABASE_ID=xxx python -m twdaily.notion
```

## 資料來源

- 股票清單與產業別：臺灣證券交易所、證券櫃檯買賣中心 OpenAPI
- 日線價格與國際指數：Yahoo Finance（`yfinance`）
- 三大法人：臺灣證券交易所
- 新聞：Google News、Yahoo 股市 RSS

> ⚠️ 本專案僅供學習研究，不構成投資建議。技術指標具落後性，請搭配基本面、籌碼面與風險控管。
