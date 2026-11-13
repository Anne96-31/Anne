# 🎫 米津玄師 GHOST 仁川場：餘票追蹤

定時重新整理 [NOL World 購票頁](https://world.nol.com/en/ticket/products/26015024)，畫面跟「全部售完」時不一樣，就用 Telegram 推播到手機，附上截圖。

- **只通知，不會自動購買**。收到通知後請自己馬上用手機或電腦去買。
- 預設每 90 秒左右檢查一次（會隨機 ±20%），最快只能設到 60 秒，以免被售票網站封鎖。
- 要在**你自己的電腦**上執行，而且電腦要一直開著。NOL 會擋雲端機房的連線，GitHub Actions 這類雲端服務跑不了。

## 一次性安裝（約 10 分鐘）

需要 Python 3.10 以上版本。在終端機（Mac 用「終端機」，Windows 用 PowerShell）進到這個資料夾後執行：

```bash
python -m pip install playwright requests
```

```bash
python -m playwright install chromium
```

## 第 1 步：設定 Telegram 通知

```bash
python watch.py telegram
```

照畫面指示操作：到 @BotFather 建立 bot、貼上 token，再傳一句話給你的 bot。手機收到「設定成功」就完成了。

## 第 2 步：登入並記下「售完」的畫面

```bash
python watch.py setup
```

會跳出一個瀏覽器視窗：

1. 用你的 NOL World 帳號登入。
2. 回到演唱會頁面，按 **Buy now**，一路點到能看到各場次、座位等級「售完」的畫面。
3. 停在那個畫面，回到終端機按 Enter。

程式會把這個畫面記成基準，之後畫面跟它不一樣就通知你。登入狀態存在 `.browser-profile/` 資料夾裡，所以平常不用重新登入。

## 第 3 步：測試一次

```bash
python watch.py check --show
```

會打開瀏覽器跑一次檢查，畫面上應該顯示「沒有變化（仍售完）」。截圖存在 `screenshots/` 資料夾。

## 第 4 步：開始追蹤

```bash
python watch.py run
```

讓這個視窗一直開著，按 Ctrl+C 停止。開始、偵測到變化、登入過期、連續出錯時，都會傳 Telegram 給你。

**記得讓電腦不要睡眠：**
- Mac：改用 `caffeinate -i python watch.py run` 執行
- Windows：設定 → 系統 → 電源 → 睡眠設為「永不」

## 通知的意思

| 訊息 | 意思 | 你要做的事 |
|---|---|---|
| 🎫 可能有餘票！ | 出現「剩餘座位」之類的字樣，或「售完」字樣變少 | 馬上去買 |
| 👀 購票畫面有變化 | 畫面變了，但不確定是不是有票 | 看截圖判斷 |
| ⚠️ 登入過期 | NOL 把你登出了 | 重新執行 `python watch.py setup` |

同一個畫面只會通知一次。誤報太多的話，在**沒有變化**的時候重跑 `setup`，更新基準畫面。

## 搶退票小提醒

- 最容易出現退票的時間：退票手續費調漲的前一天（大約演出前 10、7、3 天），以及演出前一天取消截止前後。
- 這兩天可以改成 `python watch.py run --interval 60`。
- 購票截止時間：2027-01-16 11:00（韓國時間）。

## 檔案

| 檔案 | 說明 | 會不會上傳到 GitHub |
|---|---|---|
| `watch.py` | 主程式 | 會 |
| `config.json` | Telegram token、基準畫面 | **不會**（已加入 .gitignore） |
| `.browser-profile/` | 瀏覽器登入狀態 | **不會** |
| `screenshots/` | 有變化時的截圖 | **不會** |
