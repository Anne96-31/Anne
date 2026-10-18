# AI & Data 每日摘要 2026-10-19（一）

> 今天這批文章的主軸是「AI 進入工程流程的日常化」與「評估方法的嚴謹性」。Claude Code 團隊把 code review 從最後的關卡改成像拼字檢查一樣的連續式自動審查，這正是 AI Engineer 要設計的 agent-in-the-loop 工作流；REA 則展示 agent 處理逆向工程這類高難度長流程任務的可能性。另一條線是資料科學基本功：Bayesian 推論、Simpson's paradox、以及 EEG 模型因受試者洩漏造成的評估膨脹——三篇都在提醒你，資料切分與因果直覺錯了，再漂亮的指標都是假的，這對要負責 RAG/LLM 評估的你是核心能力。其餘幾篇（web-edit、currentScript、autonomous wet lab）屬工具與領域應用，快速掃過即可。

## 🔥 今日必讀（2）

*直接補上你轉職缺的能力*

### [Claude Code 團隊如何做程式碼審查](https://simonwillison.net/2026/Oct/16/code-review/)
*Simon Willison's Weblog · 2026-10-16 · 相關度 5.07 · 必讀*

- **內容**：他們不再問『有沒有人讀過這段程式碼』，而是問『這個改動可能出什麼錯、該用自動還是人工檢查』，於是 review 從 PR 關卡變成像拼字檢查一樣持續進行，多數改動在人類看之前已被 Claude 審過並修正。
- **對你的意義**：這是 AI Engineer 的核心設計題：如何把 LLM 嵌入既有工程流程並定義它負責哪一層品質把關，跟 DE 寫 data quality check 的思維可直接接軌，但多了『人機分工』的設計維度。
- **今天可以做**：花 10 分鐘列出你 pipeline PR 中 3 類最常見的低階錯誤，並草擬一段 prompt 讓 LLM 在 pre-commit 階段自動檢查。
- **原文標題**：Quoting Addy Osmani, Morgan Westlee Lunt, and Qing Wang
- `#AI工作流` `#Agent` `#code review` `#人機協作`

### [EEG 模型在訓練與測試看到同一批人時](https://towardsdatascience.com/when-eeg-models-see-the-same-people-in-training-and-testing/)
*Towards Data Science · 2026-10-17 · 相關度 3.32 · 必讀*

- **內容**：探討當同一位受試者同時出現在訓練與測試集時造成的效能高估，並比較三種模型在 participant-aware 切分下的表現變化。
- **對你的意義**：這是資料洩漏的經典案例，直接對應你未來做 LLM/RAG 評估時的致命陷阱——測試集與知識庫、few-shot 範例重疊導致指標虛高。
- **今天可以做**：花 15 分鐘寫一份『評估資料切分檢查清單』，至少包含群組切分、時間切分與來源重疊三項。
- **原文標題**：When EEG Models See the Same People in Training and Testing
- `#評估` `#data leakage` `#LLMOps` `#實驗設計`

## 👀 值得快速瀏覽（3）

*掃過標題與重點即可*

### [從貝氏角度重看 Monty Hall 問題](https://towardsdatascience.com/inferring-the-host-a-bayesian-look-at-the-monty-hall-problem/)
*Towards Data Science · 2026-10-18 · 相關度 5.0 · 快速瀏覽*

- **內容**：指出『永遠換』只對特定行為模式的主持人成立，觀察幾集後就能推論出你面對的是哪種主持人。
- **對你的意義**：提醒你機率結論高度依賴背後的生成假設——這正是評估 LLM 輸出、設計 A/B 與離線指標時最容易出錯的地方。
- **今天可以做**：用 5 分鐘寫下『我的評估指標隱含了哪些關於使用者行為的假設』這個問題的答案。
- **原文標題**：Inferring the Host: A Bayesian Look at the Monty Hall Problem
- `#Bayesian` `#統計直覺` `#評估`

### [兩張圖都沒錯，為何結論相反？](https://towardsdatascience.com/both-charts-are-right-so-why-do-they-disagree/)
*Towards Data Science · 2026-10-18 · 相關度 5.0 · 快速瀏覽*

- **內容**：講彙總資料可能反轉結論的統計悖論（摘要資訊有限，從描述看應為 Simpson's paradox）。
- **對你的意義**：DE 每天在做 GROUP BY 與彙總，這篇直接點出彙總層級選錯會讓指標說謊，對未來負責模型效果報告的你是必備防身術。
- **今天可以做**：找一張你做過的彙總報表，花 10 分鐘拆成子群組看結論是否一致。
- **原文標題**：Both Charts Are Right. So Why Do They Disagree?
- `#統計陷阱` `#資料分析` `#指標設計`

### [REA：AI 能真的逆向破解封閉程式碼嗎？](https://www.analyticsvidhya.com/blog/2026/10/rea-ai-agent-reverse-engineer-anything/)
*Analytics Vidhya · 2026-10-18 · 相關度 4.5 · 快速瀏覽*

- **內容**：介紹一個 AI agent 嘗試取代 Ghidra/IDA 等傳統工具，從編譯後 binary 或壓縮過的 JavaScript 中還原行為邏輯。
- **對你的意義**：是觀察 agent 如何處理長流程、多工具、需反覆驗證假設的任務範本，這種任務拆解與工具編排正是 DE 轉 AI Engineer 需要補的 agent 設計能力。
- **今天可以做**：花 15 分鐘讀文章中 agent 的流程圖，畫出它的 plan → tool call → verify 迴圈。
- **原文標題**：Reverse Engineer Anything (REA): Can AI Really Crack Closed Code?
- `#Agent` `#tool use` `#逆向工程`

## 🗂️ 存起來參考（3）

*之後需要時再回頭看*

### [web-edit 0.1a2 發布](https://simonwillison.net/2026/Oct/17/web-edit/)
*Simon Willison's Weblog · 2026-10-17 · 相關度 4.66 · 存參考*

- **內容**：Simon Willison 的小型網頁檔案編輯工具更新，新增文字與圖片的複製到剪貼簿功能，方便跨機器透過 Tailscale 編輯檔案。
- **對你的意義**：示範了『為自己的工作流打造極小工具』的習慣，這種快速自建內部工具的能力在 AI Engineer 做實驗與 demo 時很吃香。
- **今天可以做**：花 10 分鐘想一個自己每週重複做的手動步驟，記下能否用 50 行腳本自動化。
- **原文標題**：web-edit 0.1a2
- `#開源工具` `#個人生產力`

### [讓 AI agent 接地於生物實驗現實](https://research.google/blog/grounding-ai-agents-in-biological-reality-building-blocks-for-autonomous-wet-labs/)
*Google Research Blog · 2026-10-16 · 相關度 4.53 · 存參考*

- **內容**：Google Research 談為自主濕實驗室打造 AI agent 的基礎元件（摘要資訊有限，僅標示為 General Science）。
- **對你的意義**：是 agent 與真實世界系統整合（感測、執行、回饋驗證）的案例，對理解 agent grounding 與可靠性設計有參考價值，但與你近期轉職任務距離較遠。
- **今天可以做**：收藏連結，之後研究 agent tool-use 與環境回饋設計時再回來細讀。
- **原文標題**：Grounding AI agents in biological reality: Building blocks for autonomous wet labs
- `#Agent` `#科學研究` `#grounding`

### [用 document.currentScript 做行內渲染](https://simonwillison.net/2026/Oct/17/document-currentscript/)
*Simon Willison's Weblog · 2026-10-17 · 相關度 4.2 · 存參考*

- **內容**：介紹利用 document.currentScript 讓 inline script 自我替換，形成一個極簡的樣板語言技巧。
- **對你的意義**：純前端技巧，與 AI Engineer 轉職主線關聯低，頂多在自建 LLM demo 頁面時用得上。
- **今天可以做**：略過，或存為做輕量 demo 頁時的小技巧備查。
- **原文標題**：Inline rendering with document​.currentScript
- `#JavaScript` `#前端技巧`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [1]，用 10 分鐘把『連續式 AI review』的概念對照到你現有的 Airflow/dbt PR 流程，寫下 3 個可以讓 LLM 先行檢查的規則（如 schema 變更、SQL 全表掃描）。
2. 讀 [8]，10 分鐘整理『資料洩漏 (leakage) 與分組切分』筆記，並延伸寫出 RAG 評估中對應的陷阱：同一份文件同時出現在 few-shot 範例與測試題庫。
3. 快速掃 [3] Simpson's paradox 與 [2] Bayesian 視角，各花 5 分鐘，記下一個你過去 dashboard 中可能被彙總資料誤導的實例。

---

掃描 13 篇，收錄 8 篇。來源分布：Simon Willison's Weblog × 3、Towards Data Science × 3、Google Research Blog × 1、Analytics Vidhya × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-10-19 01:26 自動產生 · 摘要引擎：Claude（claude-opus-5）*