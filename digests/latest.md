# AI & Data 每日摘要 2026-11-16（一）

> 今天的主軸很明顯：產業重心已從「模型本身」移到「模型外層的基礎設施」——agent runtime、gateway、inference engine、瀏覽器引擎與稽核工具（[2][5][8]）。對 Agent 系統而言，冷啟動延遲、session 狀態管理與成本控制正成為正式的架構課題（[5][6]），這些本質上是 DE 熟悉的「批次/串流資源調度」問題換了外衣。另一條線是 RAG 的進化：從向量檢索走向 Agentic GraphRAG，用知識圖譜承載決策與上下文記憶（[1]）。工具面則出現「用現有資料工具直接接 LLM」的輕量路線，local model + OpenAI-compatible endpoint 已是標配（[3]）。

## 🔥 今日必讀（3）

*直接補上你轉職缺的能力*

### [實戰指南：6 種 Agentic GraphRAG 模式](https://towardsdatascience.com/a-practitioners-guide-to-6-agentic-graphrag-patterns/)
*Towards Data Science · 2026-11-15 · 相關度 12.3 · 必讀*

- **內容**：介紹自主 agent 如何把靜態知識圖譜轉成會記住決策、使用者意圖與操作歷史的「Context Graph」，並歸納出 6 種實作模式。
- **對你的意義**：你熟悉 schema 設計與 join 邏輯，GraphRAG 正是把這套關聯建模能力轉成 AI 檢索架構的最短路徑；它也補上單純 vector RAG 無法處理多跳推理與狀態記憶的缺口。
- **今天可以做**：讀完 6 個 pattern 後，挑一個你現有資料倉儲的主題域，畫出 entity + relation 草圖並標註哪些是「決策記錄」節點。
- **原文標題**：A Practitioner's Guide to 6 Agentic GraphRAG Patterns
- `#GraphRAG` `#Agent` `#RAG` `#知識圖譜`

### [datasette-llm 0.1a11 支援 OpenAI 相容端點](https://simonwillison.net/2026/Nov/14/datasette-llm/)
*Simon Willison's Weblog · 2026-11-14 · 相關度 6.58 · 必讀*

- **內容**：Datasette 的 LLM 設定外掛新增 OpenAI-compatible endpoint 支援，可直接接 LM Studio、Ollama、llama.cpp 等本地模型。
- **對你的意義**：這是最低成本體驗「資料庫 + LLM」組合的方式，也讓你實際摸到 OpenAI-compatible 協定——這是日後切換自架模型與雲端 API 的關鍵抽象層。
- **今天可以做**：照文中指令用 uvx 跑一次 datasette + 本地模型，對自己的一個 SQLite 檔問一題自然語言查詢。
- **原文標題**：datasette-llm 0.1a11
- `#Datasette` `#本地模型` `#OpenAI相容API`

### [Bedrock AgentCore Runtime 的快速啟動架構模式](https://aws.amazon.com/blogs/machine-learning/architecture-patterns-for-fast-session-startup-on-amazon-bedrock-agentcore-runtime/)
*AWS Machine Learning Blog · 2026-11-13 · 相關度 5.69 · 必讀*

- **內容**：AgentCore Runtime V2 會對初始化好的環境做 snapshot 並於每個新 session 還原，使啟動時間不再隨 image 大小增長；文章說明如何量測並提供四種把工作移出首次請求的模式。
- **對你的意義**：Agent 上線後的冷啟動與 session 管理是 AI Engineer 的維運核心，而這跟你處理 Spark executor 暖機、Airflow task 啟動開銷的直覺高度互通，是最好轉移的一塊能力。
- **今天可以做**：把「如何量測 session start time」與四個 pattern 摘成一頁 checklist，標註哪幾項能對應你現有 pipeline 的優化經驗。
- **原文標題**：Architecture patterns for fast session startup on Amazon Bedrock AgentCore runtime
- `#AgentCore` `#冷啟動` `#LLMOps` `#AWS`

## 👀 值得快速瀏覽（3）

*掃過標題與重點即可*

### [2026 年 10 月 GitHub 趨勢前十名專案](https://www.analyticsvidhya.com/blog/2026/11/top-github-repositories-october-2026/)
*Analytics Vidhya · 2026-11-15 · 相關度 9.31 · 快速瀏覽*

- **內容**：盤點十月最紅的 repo，重點不在模型而在周邊層：agent runtime、skills、gateway、inference engine 與稽核工具，其中一個專案四週增加超過 41 萬星。
- **對你的意義**：這份清單等於幫你畫出 AI Engineer 的工具地圖，讓你知道該把時間投在 runtime 與 gateway 這類「可被 DE 技能遷移」的基礎設施層，而不是追模型。
- **今天可以做**：掃完清單，選 2 個 agent runtime 或 gateway 類專案加 star，並在筆記寫下它們各自解決的問題。
- **原文標題**：Top 10 GitHub Repositories Trending in October 2026
- `#開源` `#Agent` `#工具地圖`

### [在 SageMaker JumpStart 部署 OpenFold3](https://aws.amazon.com/blogs/machine-learning/openfold3-on-amazon-sagemaker-jumpstart-predict-biomolecular-structures/)
*AWS Machine Learning Blog · 2026-11-13 · 相關度 5.24 · 快速瀏覽*

- **內容**：示範從 JumpStart 部署 OpenFold3-preview 預測生物分子 3D 結構，涵蓋非同步推論、多 GPU 平行、自備 MSA 與 scale to zero 降低成本。
- **對你的意義**：生物領域可略過，但「非同步推論 + 多 GPU + scale to zero」正是大型模型部署的通用成本控制手法，值得當作部署範本學。
- **今天可以做**：只看部署架構段落，記下 async inference 與 scale-to-zero 的適用情境與觸發條件各一句。
- **原文標題**：OpenFold3 on Amazon SageMaker JumpStart: Predict biomolecular structures
- `#部署` `#非同步推論` `#成本優化` `#SageMaker`

### [Cloudflare 的 AI Agent 瀏覽器引擎 Kitesurf 開源](https://blog.cloudflare.com/kitesurf-open-source/)
*Cloudflare Blog · 2026-11-13 · 相關度 4.42 · 快速瀏覽*

- **內容**：Cloudflare 把實驗性的 AI agent 專用瀏覽器引擎 Kitesurf 開源，可本地執行或部署到 Cloudflare Workers。
- **對你的意義**：browser-use 類能力是 Agent 取得即時外部資料的重要管道，等同於你熟悉的 ingestion 層在 agent 世界的對應物，值得理解其執行與隔離模型。
- **今天可以做**：花 10 分鐘看 repo README，寫下它與一般 headless browser 在設計取向上的一個差異點。
- **原文標題**：Kitesurf is now open source
- `#Agent` `#瀏覽器自動化` `#Cloudflare` `#開源`

## 🗂️ 存起來參考（3）

*之後需要時再回頭看*

### [用 PyTorch 計算量子 ML 模型的有效維度](https://towardsdatascience.com/computing-effective-dimension-for-quantum-ml-models-in-pytorch/)
*Towards Data Science · 2026-11-15 · 相關度 6.05 · 存參考*

- **內容**：講解 effective dimension 的 local/global 變體、Fisher 估計、epsilon-ball 採樣與 log-space 穩定性，附 PennyLane 程式碼與時序實驗。
- **對你的意義**：與 LLM 應用開發的日常距離較遠，屬於模型容量度量的理論延伸，現階段轉職效益低。
- **今天可以做**：僅收藏，若日後需要量化模型表達能力時再回頭查閱。
- **原文標題**：Computing Effective Dimension for Quantum ML Models in PyTorch
- `#量子ML` `#模型理論` `#PyTorch`

### [datasette-vega 0.7 發布](https://simonwillison.net/2026/Nov/14/datasette-vega/)
*Simon Willison's Weblog · 2026-11-14 · 相關度 4.72 · 存參考*

- **內容**：Datasette 的 Vega-Lite 圖表外掛睽違 2018 年後更新，相容最新 alpha 版並可在 Datasette Lite 中運作。
- **對你的意義**：偏向資料視覺化工具更新，對 AI Engineer 能力建構幫助有限，但可作為快速展示 RAG/分析結果的輕量前端選項。
- **今天可以做**：收藏連結，日後做 demo 需要快速出圖時再試。
- **原文標題**：datasette-vega 0.7
- `#Datasette` `#視覺化`

### [Antigravity 的 /teamwork 推動科學與工程研究](https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/)
*Google Research Blog · 2026-11-13 · 相關度 3.04 · 存參考*

- **內容**：摘要資訊有限，僅見 Google Research 介紹 Antigravity 的 /teamwork 功能，標註為 Education Innovation，具體內容無法從摘要判斷。
- **對你的意義**：目前資訊不足以評估對轉職的直接價值，但多 agent 協作（teamwork）是 Agent 系統的進階主題，值得留意後續說明。
- **今天可以做**：開原文掃讀 2 分鐘，判斷是否涉及 multi-agent 協作機制，若是再加入待讀清單。
- **原文標題**：Advancing science & engineering with Antigravity’s /teamwork
- `#Google` `#multi-agent` `#資訊不足`

## 🎯 今天的 30 分鐘學習計畫

1. 先花 12 分鐘精讀 [1] 的 6 種 Agentic GraphRAG patterns，挑一種對照自己手上的某張事實表/維度表，寫下「若改成 Context Graph 會長怎樣」的 3 行筆記。
2. 用 10 分鐘照 [3] 的指令跑一次 uvx datasette + Ollama/LM Studio 的 OpenAI-compatible 設定，實測「本地模型查自家 SQLite」的最小 RAG 迴路。
3. 最後 8 分鐘掃 [5]，把「session startup time 如何量測」與四個把工作移出首次請求的 pattern 記成一頁 checklist，當作未來 Agent 上線的效能基準。

---

掃描 17 篇，收錄 9 篇。來源分布：Towards Data Science × 2、Simon Willison's Weblog × 2、AWS Machine Learning Blog × 2、Analytics Vidhya × 1、Cloudflare Blog × 1、Google Research Blog × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-16 03:51 自動產生 · 摘要引擎：Claude（claude-opus-5）*