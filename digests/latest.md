# AI & Data 每日摘要 2026-11-07（六）

> 今天這批文章有一條非常明確的主線：Agent 正在從「會聊天」走向「會做事、有記憶、受治理」。多篇（6、10、11、12、13）分別對應 agent 的記憶層（Mem0/JSON 持久化）、多工具決策迴圈、權限治理（Okta + Bedrock AgentCore + Cedar policy）與架構分類法（trigger/agent/capability/context），幾乎可拼成一套 agent 系統設計藍圖。第二條主線是「資料平台 × AI」：MCP server 讓 agent 安全存取 data lake（5）、醫院多層 agentic 架構（2）、Pinterest 的 embedding 訓練基礎建設（8），這些正是 DE 背景最容易建立差異化優勢的戰場。第三條是基礎設施與算力經濟學：SageMaker MIG GPU 切分（3）、Red Hat 主權 AI 與 Token 供應商思維（1）、耐能邊緣推論（9），提醒你 AI Engineer 的成本與部署知識同樣會被面試問到。建議今天把重心放在「agent memory + MCP 存取資料」這組直接可動手的題目。

## 🔥 今日必讀（5）

*直接補上你轉職缺的能力*

### [在 ECS Fargate 上建 Serverless MCP Server 讓 Agent 存取 Data Lake](https://aws.amazon.com/blogs/machine-learning/serverless-mcp-server-for-ai-agent-data-lake-access-on-amazon-ecs-fargate/)
*AWS Machine Learning Blog · 2026-11-06 · 相關度 12.63 · 必讀*

- **內容**：示範以 Fargate 建置 MCP server，透過 metadata 驅動讓 AI agent 安全存取企業 data lake，新增資料集只需一個 JSON 檔、不必寫整合程式碼。
- **對你的意義**：這是 DE → AI Engineer 最直接的橋樑：你的 data catalog 與權限模型可以原封不動變成 agent 的工具層，metadata-driven 的設計思路你已經很熟。
- **今天可以做**：用 15 分鐘讀架構圖，然後寫出你手上一張核心表的 MCP tool 描述 JSON（名稱、欄位語意、可用查詢範圍、權限條件）。
- **原文標題**：Serverless MCP server for AI agent data lake access on Amazon ECS Fargate
- `#MCP` `#Agent` `#Data Lake` `#AWS`

### [如何給你的 AI Agent 記憶](https://www.kdnuggets.com/how-to-give-your-ai-agent-memory)
*KDnuggets · 2026-11-06 · 相關度 12.36 · 必讀*

- **內容**：教學文，使用 OpenAI Agents SDK、Mem0 與 MCP，讓 agent 跨 session 記住使用者偏好與重要上下文。
- **對你的意義**：memory 是 agent 系統的核心設計題，也是 RAG 之外最常被面試追問的主題；用 Mem0 這種成熟方案可以快速建立你缺乏的實作經驗。
- **今天可以做**：跟著教學跑通 Mem0 的 add/search 兩個 API，把一段對話寫入再查回來，並在筆記記下它底層用了哪種儲存與檢索策略。
- **原文標題**：How to Give Your AI Agent Memory
- `#Agent Memory` `#Mem0` `#MCP` `#實作教學`

### [用 Ollama 與 Python 打造第一個多工具 AI Agent](https://towardsdatascience.com/build-your-first-multi-tool-ai-agent-with-ollama-and-python/)
*Towards Data Science · 2026-11-06 · 相關度 9.7 · 必讀*

- **內容**：入門教學，agent 在三個資料庫工具間自主選擇，依前一步結果決定下一次呼叫，並以八輪 circuit-breaker 避免卡死。
- **對你的意義**：用資料庫工具當範例，正好讓你把既有 SQL 能力直接接成 agent tool；circuit-breaker 則是 agent 可靠性設計的基本功。
- **今天可以做**：本地用 Ollama 跑通這個範例，把其中一個 tool 換成你自己的 SQL 查詢函式，觀察 agent 的工具選擇軌跡。
- **原文標題**：Build Your First Multi-Tool AI Agent with Ollama and Python
- `#Agent` `#Ollama` `#工具呼叫` `#實作教學`

### [用 Okta Cross App Access 與 Bedrock AgentCore 治理 Agent 權限](https://aws.amazon.com/blogs/machine-learning/govern-ai-agent-access-with-okta-cross-app-access-and-amazon-bedrock-agentcore-part-2/)
*AWS Machine Learning Blog · 2026-11-06 · 相關度 8.45 · 必讀*

- **內容**：Part 2 將單一受治理 agent 擴展到企業規模：AgentCore Gateway 作為唯一入口兌換 Okta 授權，Cedar policy 綁定工具權限，並以 AgentCore Observability 將每次允許／拒絕記錄到 CloudWatch。
- **對你的意義**：Agent 的身分與授權是企業導入的最大關卡，也是多數自學者的盲區；懂這塊能讓你從「會做 demo」升級到「能上線」。
- **今天可以做**：花 10 分鐘讀懂 Gateway + Cedar policy 的授權流程，畫一張四格流程圖（使用者→agent→gateway→tool）標註每步驗證什麼。
- **原文標題**：Govern AI agent access with Okta Cross App Access and Amazon Bedrock AgentCore – Part 2
- `#Agent治理` `#身分授權` `#Observability` `#AWS`

### [Amazon Quick 的 Agentic 基本元件分類法](https://aws.amazon.com/blogs/machine-learning/taxonomy-of-agentic-primitives-in-amazon-quick/)
*AWS Machine Learning Blog · 2026-11-06 · 相關度 8.24 · 必讀*

- **內容**：AWS 分享建構 Amazon Quick 時收斂出的 agent 元件分類：triggers、agents、capabilities、learned context，對應 When／What／Who／How 四個問題。
- **對你的意義**：提供一套可複用的 agent 系統設計語彙，讓你在設計與面試溝通時不會只會說「做了一個 agent」，而能講清楚架構分層。
- **今天可以做**：把這四個 primitive 抄進筆記，並用它重新描述你最近接觸過的任一自動化流程（哪個是 trigger、哪些是 capability）。
- **原文標題**：Taxonomy of agentic primitives in Amazon Quick
- `#Agent架構` `#系統設計` `#設計模式` `#AWS`

## 👀 值得快速瀏覽（5）

*掃過標題與重點即可*

### [Red Hat 年會：開放架構與主權 AI 佈局](https://techorange.com/2026/11/06/red-hat-summit-sovereign-ai/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-06 · 相關度 19.59 · 快速瀏覽*

- **內容**：Red Hat 主張 Any Model / Any Accelerator / Any Cloud，並提出企業 IT 應從 Token 消費者轉為內部 Token 供應商，以 OpenShift AI 的 MaaS 調度 GPU 與提供模型評測數據。
- **對你的意義**：「內部 Token 供應商」其實就是你熟悉的平台化思維從資料管線延伸到模型服務；DE 轉 AI Engineer 最容易被低估的能力，正是把模型當成可計量、可配額、可監控的共享資源。
- **今天可以做**：用 10 分鐘畫一張圖：把你現在的資料平台架構圖上多加一層 Model Gateway，標出 token 計量、模型路由、GPU 配額三個欄位。
- **原文標題**：以開放架構掌握 AI 主導權──Red Hat 全球巡迴年會揭企業 AI 算力、資安與主權治理新布局
- `#LLMOps` `#平台架構` `#主權AI` `#成本治理`

### [醫院 AI 的多層合規優先 Agentic 架構](https://arxiv.org/abs/2608.06112)
*arXiv cs.LG (Machine Learning) · 2026-11-06 · 相關度 15.61 · 快速瀏覽*

- **內容**：論文指出 70-80% 醫療 AI 試點無法規模化，主因是治理缺口、資料破碎與缺乏整合藍圖，並提出合規優先的多層互通 agentic 架構。
- **對你的意義**：這篇把「AI 專案失敗多半死在資料與治理而非模型」講得很清楚，剛好是 DE 背景的主場；可作為你面試時論述自身價值的現成論據。
- **今天可以做**：摘錄論文列出的失敗三因（governance、fragmented data、integration blueprint），對照你現在公司的資料現況各寫一句風險註記。
- **原文標題**：From Siloed Algorithms to Compliance-First Agentic Platforms: A Multi-Layered Architecture for Hospital AI Systems
- `#Agent架構` `#資料治理` `#法遵` `#產業落地`

### [SageMaker 推論支援 MIG 提升 GPU 使用率](https://aws.amazon.com/blogs/machine-learning/sagemaker-inference-now-supports-multi-instance-gpu-to-maximize-gpu-utilization-for-model-endpoints/)
*AWS Machine Learning Blog · 2026-11-06 · 相關度 14.2 · 快速瀏覽*

- **內容**：SageMaker Inference 新增 NVIDIA Multi-Instance GPU 支援，可將單顆 GPU 切成硬體隔離分區，每區跑不同模型，並提供與整顆舊 GPU 的效能實測對照。
- **對你的意義**：AI Engineer 面試常被問「怎麼降低推論成本」，GPU 切分與 right-sizing 是標準答案之一，這是 DE 少接觸的硬體層知識。
- **今天可以做**：花 10 分鐘讀完文中兩個 API 欄位設定，並在筆記寫下「什麼情況下該用 MIG、什麼情況該用多模型共用 endpoint」的判斷準則。
- **原文標題**：SageMaker Inference now supports Multi-Instance GPU to maximize GPU utilization for model endpoints
- `#推論部署` `#GPU` `#成本優化` `#SageMaker`

### [AI 讓品牌選網紅更細，最後一關仍得靠人](https://techorange.com/2026/11/06/marketer-influencer-ai/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-06 · 相關度 11.66 · 快速瀏覽*

- **內容**：AI 網紅搜尋與社群聆聽工具能做到極細顆粒度的條件篩選與 EMV 量化，但美學風格判斷與假粉絲辨識仍需人工把關，形成人機協作模式。
- **對你的意義**：是個很好的 human-in-the-loop 產品案例：提醒你設計 AI 應用時要明確切出「AI 做初篩、人做終審」的界線，這在評估流程設計上很實用。
- **今天可以做**：花 5 分鐘寫下你想做的 AI 應用中，哪一步該保留人工審核，以及用什麼指標決定 AI 可以自動通過。
- **原文標題**：連「有腸躁症的網紅」都找得到，AI 讓品牌選網紅更細，最後一關仍得靠人
- `#人機協作` `#AI應用案例` `#評估設計`

### [用一個 JSON 檔給 Python Agent 持久記憶](https://towardsdatascience.com/give-your-python-ai-agent-persistent-memory-with-one-json-file/)
*Towards Data Science · 2026-11-06 · 相關度 8.2 · 快速瀏覽*

- **內容**：以三個 Python class、OpenRouter key 與 gpt-4.1-mini，為 agent 加上計算機、模擬網頁搜尋與可跨重啟保存的對話記憶。
- **對你的意義**：是理解 agent memory 最低成本的版本，先搞懂 JSON 持久化，再升級到向量庫或 Mem0 時會更清楚每層在解決什麼問題。
- **今天可以做**：對照 [6] 的 Mem0 做法，寫一段比較筆記：JSON 檔記憶在什麼規模下會失效、需要換成什麼儲存方案。
- **原文標題**：Give Your Python AI Agent Persistent Memory with One JSON File
- `#Agent Memory` `#Python` `#實作教學` `#持久化`

## 🗂️ 存起來參考（4）

*之後需要時再回頭看*

### [t.Hub 國際交流會：Digital Twin 與 Physical AI](https://techorange.com/2026/11/06/thub-digital-twin-physical-ai/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-06 · 相關度 13.62 · 存參考*

- **內容**：活動預告，聚焦數位孿生與實體 AI 趨勢及台灣製造業的機會；摘要資訊有限，技術細節不多。
- **對你的意義**：若你未來想往製造／IoT 領域的 AI 應用發展，這類場域需要大量時序與感測資料管線，是 DE 技能可直接轉用的切入點。
- **今天可以做**：花 3 分鐘判斷是否報名 11/18 活動，若不相關就直接跳過，不佔用今日學習時間。
- **原文標題**：國際創投與產業領袖齊聚臺北！t.Hub 11/18 國際交流會解析 Digital Twin 與 Physical AI 趨勢
- `#活動` `#Physical AI` `#數位孿生` `#台灣產業`

### [Pinterest：安全且高效的多輪 Embedding 訓練](https://medium.com/pinterest-engineering/safe-and-efficient-multi-epoch-embedding-training-103bec2abc83?source=rss----4c5a5f6279b6---4)
*Pinterest Engineering · 2026-11-06 · 相關度 11.63 · 存參考*

- **內容**：Pinterest 工程團隊分享大型 ID embedding table 的 multi-epoch 訓練實務，涵蓋排序與檢索模型的 teacher scaling 與跨域預訓練基礎建設。
- **對你的意義**：大廠推薦系統的 embedding 基礎建設與你熟悉的大規模資料處理高度重疊，是理解 embedding 從訓練到 serving 全鏈路的好教材。
- **今天可以做**：略讀其 multi-epoch 會造成 overfitting／資料洩漏的風險說明，寫三行筆記對比它與 RAG 中 embedding 使用方式的差別。
- **原文標題**：Safe and Efficient Multi-Epoch Embedding Training
- `#Embedding` `#推薦系統` `#大廠實戰` `#訓練基礎建設`

### [耐能衝刺 Nasdaq IPO，從 AI 晶片跨足算力服務](https://techorange.com/2026/11/06/kneron-nasdaq-ipo/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-06 · 相關度 11.48 · 存參考*

- **內容**：台灣 NPU 廠耐能營收約為去年 3 倍並推進 Nasdaq 上市，策略從賣晶片延伸到企業 AI 推論、邊緣運算與主權 AI 基礎設施。
- **對你的意義**：產業動態為主，對你的價值在於理解邊緣推論與低功耗場景正在成為獨立市場，影響未來 AI Engineer 的部署選項。
- **今天可以做**：花 3 分鐘讀完，記下「雲端推論 vs 邊緣推論」各自適合的應用情境一句話即可。
- **原文標題**：耐能衝刺 Nasdaq IPO、營收達去年約 3 倍：從賣 AI 晶片跨足算力服務，瞄準什麼商機？
- `#產業動態` `#邊緣AI` `#NPU` `#台灣`

### [365 Data Science 免費課程開放至 11/20](https://www.kdnuggets.com/2026/10/365careers/free-ai-and-data-courses-with-365-data-science-100-unlimited-access-until-nov-20)
*KDnuggets · 2026-11-06 · 相關度 5.84 · 存參考*

- **內容**：KDnuggets 推廣資訊，11/20 前可無限存取 365 Data Science 的 134 門 AI 與資料課程、實作專案與證照。
- **對你的意義**：對已有 DE 基礎的你，課程多半偏入門，價值有限；但可挑選 LLM/agent 相關單元補空白。
- **今天可以做**：花 3 分鐘瀏覽課程清單，只收藏 1-2 門與 LLM 或 MLOps 相關的，其餘略過。
- **原文標題**：Free AI and Data Courses with 365 Data Science: 100% Unlimited Access until Nov 20
- `#學習資源` `#免費課程` `#職涯`

## 🎯 今天的 30 分鐘學習計畫

1. 先花 15 分鐘讀 [6] 與 [13]，把 agent memory 分成 short-term（conversation buffer）、long-term（Mem0/向量庫）、persistent store（JSON/DB）三層，寫成一頁筆記並標註各層在你熟悉的資料架構中對應什麼元件。
2. 用 10 分鐘照 [10] 跑一個 Ollama 本地 multi-tool agent 最小範例，把三個 tool 換成你自己的 SQL 查詢函式，觀察 agent 如何選工具與 circuit-breaker 機制。
3. 剩餘 5 分鐘掃過 [5] 與 [11]，在筆記寫下一句「我現有的 data lake 要暴露給 agent，需要補哪些 metadata 與權限控制」，作為下週的 side project 題目。

---

掃描 489 篇，收錄 14 篇。來源分布：TechOrange 科技報橘 × 4、AWS Machine Learning Blog × 4、KDnuggets × 2、Towards Data Science × 2、arXiv cs.LG (Machine Learning) × 1、Pinterest Engineering × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-07 04:28 自動產生 · 摘要引擎：Claude（claude-opus-5）*