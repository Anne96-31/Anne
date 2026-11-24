# AI & Data 每日摘要 2026-11-25（三）

> 今天這批文章有一條清楚主線：Agent 要能在企業真正上線，缺的不是更強的模型，而是「模型周邊的工程」——語意層／知識圖譜補業務脈絡（1）、retry 與人工接手的流程設計（4）、身分與隔離等資安邊界（3、12）、以及資料基礎建模（7）。第二條線是「小模型本地化」：用 YAML 微調小模型（9）、在單張 RTX 3090 跑本地 LLM（6），顯示低成本自建推論路徑逐漸成熟。第三條線是 Agent 與資料工具的融合，Simon Willison 的 datasette-agent/charts（5、8）示範了「讓 agent 直接操作你的資料平台」的最小可行樣貌，這正是 DE 背景最容易切入的角度。對你而言，今天的重點是：把既有的資料治理、schema、metadata 能力，翻譯成 agent 可消費的語意層與工具介面。

## 🔥 今日必讀（4）

*直接補上你轉職缺的能力*

### [知識圖譜與語意層：AI 代理的企業脈絡補丁](https://techorange.com/2026/11/24/semantic-knowledge-graph-ai/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-24 · 相關度 14.56 · 必讀*

- **內容**：報導指出 RAG 只給了相關資料，但 agent 執行任務還需要知道資料在企業中的意義與用法，語意知識圖譜正是補上這層脈絡。
- **對你的意義**：這是 DE 轉 AI Engineer 最有優勢的切入點：你已經懂 schema、血緣與業務定義，差的是把它轉成 agent 可消費的語意層而非只給 BI 用。
- **今天可以做**：挑一張你最熟的核心表，寫一份 200 字的語意描述（欄位意義、業務規則、常見誤用），當成未來 agent 的 context 範本。
- **原文標題**：建了資料湖，AI 代理為何還是看不懂業務？拆解知識圖譜在企業 AI 的新角色
- `#RAG` `#knowledge graph` `#semantic layer` `#agent`

### [AWS CEO：模型周邊工程比選哪個模型更重要](https://techorange.com/2026/11/24/ai-safety-cant-depend-emergency-brake-engineering/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-24 · 相關度 13.06 · 必讀*

- **內容**：AWS 執行長 Matt Garman 主張 AI 安全靠的不是 kill switch，而是身分、記錄、隔離等既有資安原則構成的可強制邊界。
- **對你的意義**：直接點出 AI Engineer 的核心價值不在換模型，而在系統設計與防護欄；你在資料平台的權限與稽核經驗可以直接遷移。
- **今天可以做**：寫一頁筆記列出你要給 agent 的三道邊界：身分權限、操作記錄、執行隔離，並各寫一個具體實作方式。
- **原文標題**：AI 安全不能只靠「緊急煞車」，AWS 執行長：模型周邊的工程，比選哪個模型更重要
- `#AI safety` `#系統設計` `#guardrails` `#LLMOps`

### [多代理工作流的重試策略該怎麼事先規劃](https://towardsdatascience.com/how-to-plan-retries-for-multi-agent-workflows-before-you-write-code/)
*Towards Data Science · 2026-11-24 · 相關度 12.9 · 必讀*

- **內容**：用 Mermaid 流程圖、Python dataclasses 與 retryable 旗標，在寫程式前就決定失敗的 agent 何時重試、何時轉交人工。
- **對你的意義**：你在 Airflow 已有 retry/SLA/告警的直覺，這篇幫你把它翻譯到非確定性的 agent workflow，是 DE 最快拿分的技能轉移。
- **今天可以做**：用 Mermaid 畫出一個既有 DAG 改成 agent workflow 的圖，標註每個節點 retryable 與 human handoff 條件。
- **原文標題**：How to Plan Retries for Multi-Agent Workflows Before You Write Code
- `#multi-agent` `#workflow` `#retry` `#orchestration`

### [Agentic CDP 的資料建模最佳實務（上）：資料基礎](https://www.databricks.com/blog/agentic-cdp-data-modeling-data-foundation)
*Databricks Blog · 2026-11-24 · 相關度 7.8 · 必讀*

- **內容**：Databricks 談如何為「代理式 CDP」打好資料基礎建模，從顧客行為事件（如 9 天前加入願望清單）驅動 agent 行動。摘要資訊有限。
- **對你的意義**：這是 DE 能力最直接升級成 AI 產品的案例：既有的事件表與顧客 360 建模，正是 agent 決策的輸入層。
- **今天可以做**：對照你現有的事件表，列出三個「agent 需要但目前模型缺少」的欄位或時間語意（例如事件新鮮度、狀態轉移）。
- **原文標題**：Data Modeling Best Practices for an Agentic CDP, Part 1: The Data Foundation
- `#Databricks` `#CDP` `#data modeling` `#agent`

## 👀 值得快速瀏覽（5）

*掃過標題與重點即可*

### [【科技早餐】OpenAI 攜手 Cisco 推開源資安工具 Shirudo](https://techorange.com/2026/11/25/openai-cisco-shirudo-ai-cybersecurity/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-24 · 相關度 14.22 · 快速瀏覽*

- **內容**：OpenAI 與 Cisco 推出開源專案 Shirudo，用 eBPF 讓 AI agent 分析漏洞、產生防護程式並測試，免重啟服務部署；另含 Amazon 收購 Decart 推論最佳化技術等新聞。
- **對你的意義**：展示 agent 在真實維運場景的落地樣貌（人類核准 + 可驗證部署），這種 human-in-the-loop 設計正是 AI Engineer 要負責的上線安全流程。
- **今天可以做**：花 5 分鐘掃過，筆記 Shirudo 的「agent 產出 → 自動測試 → 人工核准 → 部署」四階段，對照你自己的 pipeline 想一個可套用的點。
- **原文標題**：【科技早餐】OpenAI 聯手 Cisco 推出開源資安工具！測試不重啟服務就能阻擋漏洞攻擊
- `#agent` `#security` `#LLMOps` `#新聞`

### [在 RTX 3090 用 Unsloth Studio 本地跑 Inkling 2 Mini](https://www.kdnuggets.com/how-to-run-inkling-2-mini-locally-on-an-rtx-3090-using-unsloth-studio)
*KDnuggets · 2026-11-24 · 相關度 8.11 · 快速瀏覽*

- **內容**：介紹如何在單張 RTX 3090 以 Unsloth Studio 本地部署小型開源 LLM，主打不靠昂貴 API 也能快速推論與跑 coding agent。
- **對你的意義**：補上 DE 較陌生的 GPU 推論與本地部署手感，之後談成本、延遲與資料不出境的方案時才有底氣。
- **今天可以做**：花 10 分鐘讀設定步驟，記下量化格式、VRAM 需求與吞吐量三個關鍵參數，建立一張本地部署的成本評估表。
- **原文標題**：How to Run Inkling 2 Mini Locally on an RTX 3090 Using Unsloth Studio
- `#local LLM` `#inference` `#Unsloth` `#GPU`

### [datasette-charts 0.2a0：對話生成圖表](https://simonwillison.net/2026/Nov/24/datasette-charts/)
*Simon Willison's Weblog · 2026-11-24 · 相關度 7.7 · 快速瀏覽*

- **內容**：新圖表 plugin 整合 Datasette Agent，可用自然語言請 agent 依資料表產生圖表並在聊天中內嵌顯示，再開啟圖表編輯器微調。
- **對你的意義**：示範把資料查詢與視覺化包成 agent tool 的具體設計，是你做內部 data agent 的現成參考架構。
- **今天可以做**：看完 demo 影片後，寫下若要把你的查詢服務包成 agent tool，tool schema 的輸入輸出該怎麼定義。
- **原文標題**：datasette-charts 0.2a0
- `#datasette` `#tool use` `#visualization` `#agent`

### [Soup：用一個 YAML 檔微調小型 LLM](https://www.analyticsvidhya.com/blog/2026/11/fine-tune-small-llm-locally-with-soup/)
*Analytics Vidhya · 2026-11-24 · 相關度 7.3 · 快速瀏覽*

- **內容**：透過單一 YAML 設定檔微調小模型，用途示例是把工程師隨手寫的事故更新，強制轉成固定格式（狀態／影響／下一步）且不得捏造。
- **對你的意義**：是 DE 最容易理解的 fine-tuning 入門：本質是格式與規則的一致性，正好用你熟悉的設定檔思維切入訓練流程。
- **今天可以做**：花 15 分鐘讀完流程，並擬出一個你自己場景的微調資料範例（10 筆輸入→標準輸出），當作後續練習素材。
- **原文標題**：Soup: Fine-Tune a Small LLM with One YAML File
- `#fine-tuning` `#small LLM` `#YAML` `#structured output`

### [GPT-6.2 Astra 自主破解歷史懸案](https://simonwillison.net/2026/Nov/24/astra-historical-mystery/)
*Simon Willison's Weblog · 2026-11-24 · 相關度 5.39 · 快速瀏覽*

- **內容**：歷史教授 Mark Humphries 記錄 GPT-6.2 Astra 在極少提示下，22 分鐘內自主找出 1808 年匿名素描本的作者，過程包含提出假設並找到冷門紙本檔案佐證。
- **對你的意義**：這是深度研究型 agent 的能力上限觀察：模型能自主規劃檢索與驗證假設，提醒你 RAG 設計正從「單輪檢索」走向「多輪研究迴圈」。
- **今天可以做**：讀完後寫三句筆記：這個 agent 的規劃、檢索、驗證各做了什麼，對照你自己的 RAG 流程缺哪一段。
- **原文標題**：GPT 6.2 Astra Solves a Historical Mystery
- `#agent` `#deep research` `#case study` `#GPT`

## 🗂️ 存起來參考（5）

*之後需要時再回頭看*

### [datasette-agent 0.7a1 釋出](https://simonwillison.net/2026/Nov/24/datasette-agent/)
*Simon Willison's Weblog · 2026-11-24 · 相關度 8.66 · 存參考*

- **內容**：Simon Willison 的 Datasette Agent 小版本更新，改善 iframe 側邊面板以 fragment hash 導航，便於與其他 plugin 深度整合。摘要資訊有限。
- **對你的意義**：是「agent 直接操作資料平台」的開源實作樣本，對 DE 來說是看懂 agent 工具介面設計的最低門檻範例。
- **今天可以做**：花 5 分鐘到 agent.datasette.io 點開看一下互動方式，記下它把哪些資料操作暴露成 agent tool。
- **原文標題**：datasette-agent 0.7a1
- `#datasette` `#open source` `#agent tooling`

### [馴服真實世界的髒 CSV：pandas read_csv 實戰](https://www.kdnuggets.com/from-messy-to-clean-taming-real-world-csv-files-with-pandas-read_csv)
*KDnuggets · 2026-11-24 · 相關度 7.2 · 存參考*

- **內容**：示範如何用 pandas read_csv 的參數打造一個防彈的 Python 資料載入器，把雜亂資料整理乾淨。
- **對你的意義**：對你多半是既有技能複習，但可借來當 LLM 應用的資料前處理檢查清單（編碼、型別、缺值）以降低後續 embedding 噪音。
- **今天可以做**：快速掃過參數清單，把三個你沒用過的 read_csv 參數記下來存成 snippet。
- **原文標題**：From Messy to Clean: Taming Real-World CSV Files with pandas read_csv()
- `#pandas` `#data cleaning` `#ETL`

### [如何計算並落地顧客終身價值（CLV）](https://towardsdatascience.com/how-to-calculate-and-operationalize-customer-lifetime-value/)
*Towards Data Science · 2026-11-24 · 相關度 6.5 · 存參考*

- **內容**：介紹用 cohort churn、BTYD 模型與行為分群，把 CLV 從簡報 KPI 變成每日決策依據。
- **對你的意義**：補的是業務領域知識而非 AI 技能，但能幫你在設計 agent 或 CDP 應用時說出對的商業語言。
- **今天可以做**：存起來，若近期要做 CDP/行銷類 AI 專案再回頭讀 BTYD 模型段落。
- **原文標題**：How to Calculate and Operationalize Customer Lifetime Value
- `#CLV` `#analytics` `#business metrics`

### [Amazon Bedrock 推出 Trusted Access API](https://aws.amazon.com/blogs/machine-learning/introducing-the-amazon-bedrock-trusted-access-api-with-anthropics-enterprise-frontier-safeguards-and-enterprise-data-controls/)
*AWS Machine Learning Blog · 2026-11-24 · 相關度 6.0 · 存參考*

- **內容**：Bedrock 新增統一入口讓企業探索與申請模型供應商方案，首波公開預覽為 Anthropic 的 Enterprise Frontier Safeguards 與 Enterprise Data Controls。
- **對你的意義**：企業導入 LLM 時的資料控管與合規，是 AI Engineer 面試常被追問的點；這是你理解雲端託管模型治理機制的入口。
- **今天可以做**：花 5 分鐘看 EDC 的資料控管說明，筆記「企業用 Claude 時資料去哪、如何控管」的一句話答案。
- **原文標題**：Introducing the Amazon Bedrock Trusted Access API, with Enterprise Frontier Safeguards and Enterprise Data Controls for Claude models
- `#Bedrock` `#governance` `#enterprise` `#Claude`

### [強化 Transformer 的殘差連接](https://research.google/blog/supercharging-transformer-residual-connections/)
*Google Research Blog · 2026-11-23 · 相關度 5.34 · 存參考*

- **內容**：Google Research 探討改良 Transformer 殘差連接的演算法與理論工作。摘要資訊極為有限。
- **對你的意義**：屬於模型底層研究，對日常 LLM 應用開發非必要，但有助於你在面試時談得出架構層級的理解。
- **今天可以做**：存入待讀清單，今天只花 3 分鐘看圖表結論，確認是否影響推論成本或長序列表現。
- **原文標題**：Supercharging transformer residual connections
- `#transformer` `#research` `#架構`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [1] 知識圖譜／語意層那篇，花 10 分鐘把你現在負責的一張核心事實表，寫成一份 agent 可讀的語意描述（欄位含義、業務規則、常見錯用情境），這就是 RAG/Agent 的 context 來源。
2. 再讀 [4] multi-agent retry 設計，花 10 分鐘用 Mermaid 畫出一個你熟悉的 pipeline 改成 agent workflow 的流程圖，標出每個節點 retryable / 需人工介入。
3. 最後花 10 分鐘掃 [5][8] 的 datasette-agent demo 影片與 [3] AWS 的安全工程觀點，筆記一條「agent 操作資料庫時我要加哪些邊界（權限、唯讀、記錄）」。

---

掃描 62 篇，收錄 14 篇。來源分布：TechOrange 科技報橘 × 3、Simon Willison's Weblog × 3、Towards Data Science × 2、KDnuggets × 2、Databricks Blog × 1、Analytics Vidhya × 1、AWS Machine Learning Blog × 1、Google Research Blog × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-25 07:33 自動產生 · 摘要引擎：Claude（claude-opus-5）*