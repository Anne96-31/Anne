# AI & Data 每日摘要 2026-11-13（五）

> 今天這批文章集中在三個訊號：一是 Agent 從 demo 走向 production 的工程化（AWS Agent DLC、A2A 多代理協定、Pinterest 的 Loop Engineering），評估與合規流程成為新的 CI/CD 核心；二是 RAG 的現實檢驗——當干擾段落擴張到百萬級時檢索品質崩跌 40 分，加上 GraphRAG 的興起，顯示「資料品質與檢索架構」才是 AI 應用勝負點，這正是 DE 的主場；三是成本與 ROI 的焦慮全面浮現（VB Pulse 調查、製造業算力論壇、LLM inference metrics），企業要的是能把 token 帳單與延遲指標算清楚的工程師。對 DE 轉職者而言，今天的主軸就是：把 pipeline 能力延伸到 retrieval 品質、agent 評估迴圈與推論成本量測這三個介面。

## 🔥 今日必讀（7）

*直接補上你轉職缺的能力*

### [Google Gemini Decision 1 決策模型登場](https://techorange.com/2026/11/12/google-gemini-decision-1-api/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-12 · 相關度 13.33 · 必讀*

- **內容**：Google 推出不以生成文字為主、直接對候選選項評分並回傳信心分數的 Gemini Decision 1，單次呼叫最多評估 1,000 項獨立判斷，支援多模態。
- **對你的意義**：決策模型把「分類／路由／評分」從 LLM 生成中拆出來，這類批次高吞吐的判斷任務跟 DE 熟悉的批次資料處理極像，是你能快速切入的 AI 應用型態。
- **今天可以做**：挑一個你現有 pipeline 中的規則式分類欄位（例如資料品質標記），設計成「是非題 + 信心分數」的 decision model prompt 規格草稿。
- **原文標題**：Google 的決策模型來了：Gemini Decision 1 一次評估千項問題，與 Jev 有何不同？
- `#決策模型` `#Gemini` `#多模態` `#分類路由`

### [Pinterest 如何用 Loop Engineering 提升 Agent 合規性](https://medium.com/pinterest-engineering/how-pinterest-improved-analytics-agent-compliance-with-loop-engineering-d3c52d0abaa2?source=rss----4c5a5f6279b6---4)
*Pinterest Engineering · 2026-11-12 · 相關度 13.16 · 必讀*

- **內容**：Pinterest 的 Analytics Agent 需在正確時機執行正確步驟，團隊以 Loop Engineering 提升 agent 的「compliance」以讓答案更一致。
- **對你的意義**：這是資料分析型 agent 的真實案例——它要搜尋公司資料生態系並回答查詢延遲類問題，幾乎是 DE 工作的 agent 化，最貼近你的轉職落點。
- **今天可以做**：讀完後列出 Pinterest 定義 compliance 的方式，並為「查詢自家 data warehouse 的 agent」寫下 5 個必要步驟檢查清單。
- **原文標題**：How Pinterest Improved Analytics Agent Compliance with Loop Engineering
- `#Analytics Agent` `#評估` `#大廠實戰`

### [用 graphrag-toolkit 打造圖強化 GenAI 應用](https://www.kdnuggets.com/building-graph-enhanced-genai-applications-with-graphrag-toolkit)
*KDnuggets · 2026-11-12 · 相關度 12.08 · 必讀*

- **內容**：說明 graph-enhanced RAG 如何串起純向量檢索會漏掉的關聯事實，並用 AWS Labs 的 graphrag-toolkit、Neo4j 與 pgvector 做多跳研究助理。
- **對你的意義**：GraphRAG 本質是建模與 ETL 問題（實體抽取、關係表、索引），DE 的資料建模經驗可直接遷移，是差異化優勢最高的 RAG 進階主題。
- **今天可以做**：用 pgvector 或本機 Neo4j 跑一次 toolkit 的 quickstart，或至少畫出你某個領域資料的 entity-relation 圖草稿。
- **原文標題**：Building Graph-Enhanced GenAI Applications with graphrag-toolkit
- `#GraphRAG` `#Neo4j` `#pgvector` `#資料建模`

### [從原型到上線：用 Agent DLC 做 Agent 工程](https://aws.amazon.com/blogs/machine-learning/from-prototype-to-production-engineering-agents-with-agent-dlc/)
*AWS Machine Learning Blog · 2026-11-12 · 相關度 11.48 · 必讀*

- **內容**：指出 agent 卡在 demo 與發布之間的原因是缺乏可重複的品質衡量方式，提出 agent 打破傳統 CI/CD 的三個特性，以及 Agent DLC 的一套生命週期、兩個迴圈與一個判準。
- **對你的意義**：你熟悉資料 pipeline 的 CI/CD 與資料測試，這篇正好補上「非確定性系統該怎麼做回歸測試」的空缺，是 AI Engineer 面試常考的 LLMOps 核心。
- **今天可以做**：把文中「aggregate metric 掩蓋覆蓋缺口」的案例寫成筆記，並想一個你會如何用分層切片指標避免同樣盲點。
- **原文標題**：From prototype to production: Engineering agents with Agent DLC
- `#LLMOps` `#Agent 評估` `#CI/CD`

### [AI 預算加碼但 ROI 說不清：38% 專案曾因超支受挫](https://techorange.com/2026/11/11/ai-project-cost-overruns-vb-pulse/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-11 · 相關度 9.73 · 必讀*

- **內容**：VB Pulse 調查 156 位 AI 從業者，38% 的組織過去一年因成本超支延後／縮減／取消 AI 專案，僅 26% 用財務報酬衡量支出，且 57% 的 GPU 營運者平均使用率在 50% 以下。
- **對你的意義**：成本與使用率的量測正是 DE 最擅長的「指標與報表」工作，把 token/GPU 成本做成可觀測儀表板，是你進 AI 團隊後最快展現價值的切入點。
- **今天可以做**：設計一張 AI 成本觀測表的欄位草稿（每請求 token 數、單位成本、使用率、對應業務指標），想好資料從哪裡抓。
- **原文標題**：AI 預算還要加碼，投資報酬卻說不清：38% 受訪者曾因超支延後、縮減或取消專案
- `#AI ROI` `#成本管理` `#FinOps`

### [5 分鐘搞懂 9 個 LLM 推論關鍵指標](https://www.kdnuggets.com/9-key-llm-inference-metrics-explained-in-5-minutes)
*KDnuggets · 2026-11-11 · 相關度 9.34 · 必讀*

- **內容**：解說量測 LLM 推論效能的關鍵指標與公式，涵蓋延遲、token 產生速度與系統負載。
- **對你的意義**：TTFT、TPOT、throughput 這些是 AI Engineer 的日常語言，補齊後你才能在容量規劃與成本討論中和 ML/平台團隊對話。
- **今天可以做**：把 9 個指標做成一頁 cheat sheet，並標註哪些可從你現有監控系統（如 Prometheus）直接延伸採集。
- **原文標題**：9 Key LLM Inference Metrics Explained in 5 Minutes
- `#推論效能` `#延遲指標` `#監控`

### [干擾段落增至 268 萬時 RAG 檢索掉了 40 分](https://towardsdatascience.com/rag-retrieval-lost-40-points-when-distracting-passages-grew-to-268m/)
*Towards Data Science · 2026-11-12 · 相關度 8.2 · 必讀*

- **內容**：以可重現實驗比較 BM25、embedding 與 parent document 檢索，顯示干擾段落規模擴大時檢索品質大幅下滑，並指出自撰評測會高估搜尋效果、答案在 context 中的位置也有影響。
- **對你的意義**：這直指 RAG 從 demo 到真實語料規模的斷崖，正好是 DE 能貢獻之處：資料規模、切分策略與評測集設計都是你的強項領域。
- **今天可以做**：把自己的小型 RAG 測試集刻意混入大量不相關文件，重跑一次 recall@k 並記錄下降幅度。
- **原文標題**：RAG Retrieval Lost 40 Points When Distracting Passages Grew to 2.68M
- `#RAG` `#檢索評估` `#BM25` `#embedding`

## 👀 值得快速瀏覽（4）

*掃過標題與重點即可*

### [製造業 AI 規模化：算力之外的數據治理](https://techorange.com/2026/11/12/tisi-hpe-pegatron-ai-cdc/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-12 · 相關度 18.26 · 快速瀏覽*

- **內容**：大世科、HPE、和碩與學界討論製造業如何把 AI 算力投資轉成可規模化效益，強調流程、知識庫、電力散熱與數據治理。
- **對你的意義**：文中點明「算力與演算法迭代快，真正握在企業手中的是數據」，這正是 DE 背景轉 AI Engineer 的最大籌碼——把資料治理能力包裝成 AI 落地的前置條件。
- **今天可以做**：花 10 分鐘寫下你現有 pipeline 中有哪三類資料可直接變成企業知識庫的來源，以及各自缺什麼治理（權限、版本、品質）。
- **原文標題**：「如何讓燒掉的 Token 轉化為企業競爭力？」大世科、HPE、和碩解析製造業 AI 規模化關鍵
- `#台灣產業` `#數據治理` `#AI 落地`

### [用 Amazon Bedrock 與 Spring AI 打造自主 Agent](https://aws.amazon.com/blogs/machine-learning/build-autonomous-ai-agents-with-amazon-bedrock-and-spring-ai/)
*AWS Machine Learning Blog · 2026-11-12 · 相關度 14.58 · 快速瀏覽*

- **內容**：示範 Java 開發者如何用 Bedrock + Spring AI 實作 tool calling、對話記憶、韌性模式與多 agent 編排，並以 AgentCore 部署。
- **對你的意義**：對 DE 來說重點不是 Java，而是「tool calling + memory + resilience + orchestration」這組 production agent 的標準零件清單，可直接對照你熟悉的工作流編排思維。
- **今天可以做**：把文中提到的四個 agent 元件（tool calling、memory、resilience、orchestration）各寫一句話定義，並對照 Airflow 的 task/retry/XCom 做類比筆記。
- **原文標題**：Build autonomous AI agents with Amazon Bedrock and Spring AI
- `#Agent` `#Bedrock` `#架構模式`

### [用 A2A 協定建可組合的多代理系統](https://aws.amazon.com/blogs/machine-learning/build-composable-interoperable-multi-agent-systems-with-a2a-on-aws/)
*AWS Machine Learning Blog · 2026-11-12 · 相關度 14.48 · 快速瀏覽*

- **內容**：介紹在 AWS 上以 Agent-to-Agent (A2A) 協定，讓 ECS 上的 LangChain orchestrator 與 Bedrock AgentCore 上的 Strands agent 跨組織邊界互通，雙向且 OAuth 驗證。
- **對你的意義**：A2A 是 agent 世界的介面標準化嘗試，概念上類似資料界的 schema contract；理解它能讓你在設計跨團隊 AI 系統時不被單一框架綁死。
- **今天可以做**：花 10 分鐘查 A2A 的 Agent Card 規格，寫下它與 MCP 的分工差異（誰接工具、誰接 agent）。
- **原文標題**：Build composable, interoperable multi-agent systems with A2A on AWS
- `#A2A` `#Multi-agent` `#互通協定`

### [7 本免費書帶你學會打造 AI 系統](https://www.kdnuggets.com/7-free-books-to-learn-about-building-ai-systems)
*KDnuggets · 2026-11-12 · 相關度 11.06 · 快速瀏覽*

- **內容**：整理 7 本免費書籍，聚焦把 AI agent 從「能動」推到「能在 production 穩定運作」所需的工程知識。
- **對你的意義**：轉職最缺的往往不是會串 API，而是系統性的 AI 工程知識地圖，這份書單可當你 1–3 個月的自學骨架。
- **今天可以做**：掃完書單後挑 1 本與 agent 上線或評估最相關的，下載並排進本週讀書計畫的前兩章。
- **原文標題**：7 FREE Books to Learn About Building AI Systems
- `#學習資源` `#書單` `#AI 系統`

## 🗂️ 存起來參考（3）

*之後需要時再回頭看*

### [3D 生成模型 Fine-Tuning 指南](https://huggingface.co/blog/3d-lora-finetuning)
*Hugging Face Blog · 2026-11-12 · 相關度 11.1 · 存參考*

- **內容**：Hugging Face 關於 3D 生成模型 LoRA fine-tuning 的教學文章；摘要資訊有限，僅能依標題判斷。
- **對你的意義**：3D 生成與你的轉職主線（LLM 應用、RAG、Agent）相關性低，但 LoRA 的訓練流程概念可供日後需要微調時參考。
- **今天可以做**：先存書籤，只花 2 分鐘確認文中 LoRA 設定的參數名稱（rank、alpha）是否與文字模型一致。
- **原文標題**：The Definitive Fine-Tuning Guide for 3D Generation Models
- `#Fine-tuning` `#LoRA` `#3D`

### [用 coding agent 遷移到 Bedrock 託管知識庫](https://aws.amazon.com/blogs/machine-learning/migrate-to-amazon-bedrock-managed-knowledge-base-with-your-coding-agent/)
*AWS Machine Learning Blog · 2026-11-12 · 相關度 9.99 · 存參考*

- **內容**：介紹 amazon-bedrock skill 的遷移指南，讓 coding agent 以唯讀探勘規劃、並行建立新知識庫或 IaC 模板，並在切換前驗證檢索結果。
- **對你的意義**：「先唯讀探勘、平行建置、切換前驗證」正是資料遷移的經典 pattern，看它如何套用在知識庫上，可幫你把 DE 的遷移經驗翻譯成 RAG 維運語言。
- **今天可以做**：用 15 分鐘寫下一份 RAG 知識庫遷移檢查表，至少包含檢索結果比對（retrieval parity）的驗證方法。
- **原文標題**：Migrate to Amazon Bedrock Managed Knowledge Base with your coding agent
- `#Bedrock` `#Knowledge Base` `#遷移` `#IaC`

### [用 R 讀交叉配對相關性避免假性排斥（第三篇）](https://towardsdatascience.com/how-to-read-cross-pair-correlation-in-r-without-fake-repulsion-part-3/)
*Towards Data Science · 2026-11-12 · 相關度 6.5 · 存參考*

- **內容**：以模擬疤痕與 31 隻動物缺血後資料，說明非齊性估計量、random labelling 與 brms 如何區分組織損失與真實交互作用。
- **對你的意義**：屬生醫空間統計領域，與 AI Engineer 轉職主線幾乎無關，僅在你需要嚴謹統計推論設計時可借鏡其實驗控制思路。
- **今天可以做**：略過即可，若有興趣可花 3 分鐘看它如何設計對照以排除假訊號。
- **原文標題**：How to Read Cross Pair Correlation in R Without Fake Repulsion (Part 3)
- `#空間統計` `#R` `#生醫`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [13] RAG 檢索崩跌實驗，動手把自己手邊任一份文件集擴充 10 倍干擾資料，重跑一次 BM25 vs embedding 的 recall@k，記錄分數變化（15 分鐘）。
2. 讀 [7] Agent DLC 與 [5] Pinterest Loop Engineering，用 10 分鐘寫一份「Agent 評估規格」筆記：定義三個通過標準（compliance 步驟、aggregate metric 的覆蓋盲點、回歸判準）。
3. 掃 [12] 九個 LLM inference 指標，把 TTFT、TPOT、throughput、cost per 1K tokens 填成一張可套用的表格，對照 [11] 的 ROI 問題，想一個自家 pipeline 的成本量測點（5 分鐘）。

---

掃描 83 篇，收錄 14 篇。來源分布：AWS Machine Learning Blog × 4、TechOrange 科技報橘 × 3、KDnuggets × 3、Towards Data Science × 2、Pinterest Engineering × 1、Hugging Face Blog × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-13 05:30 自動產生 · 摘要引擎：Claude（claude-opus-5）*