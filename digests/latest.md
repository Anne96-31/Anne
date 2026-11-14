# AI & Data 每日摘要 2026-11-15（日）

> 今天這批文章有一條清楚主軸：Agent 已經從「能不能做」進入「上線後怎麼管、怎麼省錢」的階段。Towards Data Science 的 100+ agent 觀測指出失敗多半是 silent drift（品質、token、延遲先出訊號），而不是明顯的 error；AWS 則一次給出 Bedrock 推論成本的四個 request-level 旋鈕，以及用 LiteLLM + NeMo Switchyard 做 model routing、以「cost per solved task」而非 per token 計價的實作。Natera 的 AgentCore 案例則示範了從 knowledge base 建置到 evaluation 的完整 agentic 架構。對 DE 轉 AI Engineer 來說，這正是你的優勢區：監控、成本歸因、pipeline 重用的思維可以直接平移到 LLMOps。其餘像 Gartner 2027 趨勢、NVIDIA 治理變動、機器人落地則屬於產業脈絡層面的背景閱讀。

## 🔥 今日必讀（5）

*直接補上你轉職缺的能力*

### [GS Caltex 用 SageMaker Canvas 打造生產級 MLOps（上）](https://aws.amazon.com/blogs/machine-learning/production-mlops-at-gs-caltex-with-amazon-sagemaker-canvas-part-1/)
*AWS Machine Learning Blog · 2026-11-13 · 相關度 10.58 · 必讀*

- **內容**：GS Caltex 把 no-code 的 SageMaker Canvas 模型接到 SageMaker Pipelines，讓驗證過的前處理流程與模型可重複使用，部署時間從約一週縮到數小時，並每 30 分鐘跑一次 batch inference。
- **對你的意義**：這是 DE 最容易切入 MLOps 的角度：把 pipeline 重用、排程與批次推論工程化，正是你既有 Airflow/Spark 技能的直接延伸。
- **今天可以做**：對照這篇的架構，畫一張圖說明你現有的 Airflow DAG 若要承接模型推論，需要補上哪些步驟（模型版本、前處理一致性、結果落地）。
- **原文標題**：Production MLOps at GS Caltex with Amazon SageMaker Canvas, part 1
- `#MLOps` `#SageMaker` `#batch inference` `#資料管線`

### [100+ AI Agent 數據：失敗來自無聲漂移而非錯誤](https://towardsdatascience.com/data-from-100-ai-agents-shows-they-fail-by-silent-drift-not-errors/)
*Towards Data Science · 2026-11-14 · 相關度 10.03 · 必讀*

- **內容**：觀察 100 多個 AI agent 發現，品質與 token 異常在 38% 的案例中是早期訊號，而 error 只佔約 1%，因此監控應從 quality、cost、latency 著手。
- **對你的意義**：DE 習慣用 error rate 與 SLA 監控 pipeline，但 agent 的失敗是靜默退化，你必須學會設計語意層面的品質指標，這是轉職最關鍵的觀念落差。
- **今天可以做**：把 quality / cost / latency 三類訊號各設計 2 個可量化指標，寫成一份 agent 監控草案筆記。
- **原文標題**：Data From 100+ AI Agents Shows They Fail by Silent Drift, Not Errors
- `#LLMOps` `#agent 監控` `#drift` `#評估`

### [用 NeMo Switchyard 在 Bedrock 上做 coding agent 路由](https://aws.amazon.com/blogs/machine-learning/route-coding-agent-requests-to-the-right-model-on-amazon-bedrock-with-nvidia-nemo-switchyard/)
*AWS Machine Learning Blog · 2026-11-13 · 相關度 7.4 · 必讀*

- **內容**：用 AWS CDK 部署 LiteLLM 搭配 NVIDIA NeMo Switchyard routing plugin，並以「每個已解決任務的成本」而非每 token 價格，比較 routed model group 與單一模型基準。
- **對你的意義**：model routing 是 AI Engineer 控制成本的核心技能，而「cost per solved task」這種以結果為單位的成本歸因，正好能套用你在資料倉儲做成本分攤的經驗。
- **今天可以做**：在本機用 LiteLLM 設定一組「便宜模型優先、失敗才升級」的簡易 routing config，並記錄兩種路徑的成本差異假設。
- **原文標題**：Route coding agent requests to the right model on Amazon Bedrock with NVIDIA NeMo Switchyard
- `#model routing` `#LiteLLM` `#Bedrock` `#成本優化`

### [影響 Amazon Bedrock 成本的四個推論選項](https://aws.amazon.com/blogs/machine-learning/four-amazon-bedrock-inference-choices-that-affect-cost/)
*AWS Machine Learning Blog · 2026-11-12 · 相關度 6.9 · 必讀*

- **內容**：指出即使調好 prompt 與應用邏輯，帳單仍可能上升；cache duration、service tier、reasoning effort、maxTokens 這四個 request-level 選項會改變處理的 token 數與計費費率，並說明如何驗證效果。
- **對你的意義**：AI Engineer 面試與實務都會被問「怎麼把推論成本砍下來」，這四個旋鈕是可立即操作的具體答案，比空談 prompt 優化更有說服力。
- **今天可以做**：把四個參數整理成一張對照表（調整方向 / 影響 token 數 / 影響品質風險），存成你的成本優化 checklist。
- **原文標題**：Four Amazon Bedrock inference choices that affect cost
- `#推論成本` `#Bedrock` `#prompt caching` `#LLMOps`

### [Natera 用 Bedrock AgentCore 打造實驗室營運 agent 系統](https://aws.amazon.com/blogs/machine-learning/how-natera-designed-an-agentic-ai-system-for-lab-ops-with-amazon-bedrock-agentcore/)
*AWS Machine Learning Blog · 2026-11-12 · 相關度 6.73 · 必讀*

- **內容**：Natera 建立名為 SWARM 的 agentic 系統，從 knowledge base 建置到部署與評估完整說明，宣稱首次回應速度快約 130 倍、支援工單自動覆蓋率達 96.2%。
- **對你的意義**：這是少見把 knowledge base → deployment → evaluation 整條鏈講完的實戰文，剛好補上你從資料管線跨到 RAG/Agent 系統設計的架構視野。
- **今天可以做**：讀架構段落，畫出它的資料流圖，並標註「知識庫更新」這一段若由你來做，會如何用現有 ETL 工具實作。
- **原文標題**：How Natera designed an agentic AI system for lab ops with Amazon Bedrock AgentCore
- `#Agent 架構` `#RAG` `#knowledge base` `#評估`

## 👀 值得快速瀏覽（4）

*掃過標題與重點即可*

### [Gartner 2027 十大科技趨勢：軟體極度豐富與用完即拋](https://techorange.com/2026/11/14/gartner-trends-for-2027/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-13 · 相關度 13.19 · 快速瀏覽*

- **內容**：Gartner 預測生成式 AI 與 vibe coding 帶來「軟體極度豐富」，2030 年領先企業 80% 新應用將是短期任務導向的 disposable applications。
- **對你的意義**：當應用可以隨需生成又快速下線，AI Engineer 的價值會從「寫程式」移到「定義平台規則、治理與除役標準」，這跟 DE 熟悉的資料治理、lineage 思維高度相通。
- **今天可以做**：花 10 分鐘列出你目前負責的 3 條 pipeline，判斷哪些屬於「核心主幹」、哪些其實可以用臨時生成的腳本取代。
- **原文標題**：【Gartner 2027 十大科技趨勢報告】AI 開發工具引爆軟體極度豐富，2030 年 80% 新軟體將轉為「用完即拋」
- `#產業趨勢` `#平台工程` `#AI 治理`

### [Helsing 推 Clarity 挑戰 Palantir，數百 AI 代理交叉比對情報](https://techorange.com/2026/11/13/helsing-clarity-palantir-maven-rival/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-13 · 相關度 10.58 · 快速瀏覽*

- **內容**：德國 Helsing 發表軍用情報平台 Clarity，以數百個 AI agent 交叉比對戰場情報、交戰授權仍保留給人類，訴求歐洲資料主權與不依賴美國基礎設施。
- **對你的意義**：展示了大規模 multi-agent 系統中「human-in-the-loop 授權」與「資料主權／部署位置」的設計考量，這在金融、醫療等敏感產業的 AI 專案同樣會被追問。
- **今天可以做**：用 3 行筆記寫下：你未來的 agent 系統中，哪一個決策點必須強制保留人類審核？理由是什麼？
- **原文標題**：Helsing 推 Clarity 挑戰 Palantir，稱數百個 AI 代理交叉比對情報、交戰仍由人類授權
- `#multi-agent` `#human-in-the-loop` `#資料主權` `#產業趨勢`

### [鴻海如何讓人形機器人進工廠：先拆任務再決定哪段需要 AI](https://techorange.com/2026/11/13/foxconn-humanoid-robotics-leo-kuo/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-13 · 相關度 9.42 · 快速瀏覽*

- **內容**：鴻海郭柳宗分享以 SMT 產線與倉儲為切入點，先用輪式平台把特定任務做成熟，並指出 VLA 模型在速度與誤差上仍不足以完全取代精準力控。
- **對你的意義**：「先拆任務、再決定哪一段需要 AI」是導入 LLM/Agent 時同樣適用的方法論，可避免把整條流程都丟給模型而難以評估。
- **今天可以做**：挑一個你熟悉的業務流程，拆成 5 個子任務，標註哪一段真的需要 LLM、哪一段用規則或 SQL 更穩。
- **原文標題**：鴻海怎麼讓人形機器人進工廠？郭柳宗：先拆任務，再決定哪一段需要 AI
- `#AI 落地` `#任務拆解` `#機器人` `#VLA`

### [黃仁勳辭任後的 NVIDIA：供應鏈與對中管制變數](https://techorange.com/2026/11/13/nvidia-after-jensen-huang-governance-export-controls/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-13 · 相關度 6.81 · 快速瀏覽*

- **內容**：NVIDIA 董事會宣布黃仁勳辭去執行長與董事職務、由 CFO 柯蕾絲暫代，報導指其市值自首波報導以來蒸發約 1.4 兆美元，接班與美國對中晶片管制走向成為焦點。
- **對你的意義**：算力供應與出口管制會直接影響你未來可用的模型與 GPU 成本結構，屬於需要知道但不必深究的產業背景。
- **今天可以做**：花 3 分鐘掃過，記下一個問題：若 GPU 供給收緊，你的 AI 應用有哪些 fallback 模型選項？
- **原文標題**：黃仁勳辭任後的 NVIDIA：供應鏈合作能否延續？華府對中晶片管制恐再收緊
- `#產業動態` `#NVIDIA` `#算力供應`

## 🗂️ 存起來參考（5）

*之後需要時再回頭看*

### [用 NumPy 在 Python 建立 Markov Chain](https://towardsdatascience.com/how-to-build-a-markov-chain-in-python-with-numpy/)
*Towards Data Science · 2026-11-14 · 相關度 7.41 · 存參考*

- **內容**：逐步教學 transition matrix、Chapman–Kolmogorov 方程與 stationary distribution，以三狀態寫作範例貫穿。
- **對你的意義**：狀態轉移的思維對理解 agent 的狀態機設計與行為機率建模有幫助，但對短期轉職不是優先項目。
- **今天可以做**：收藏起來，之後設計 agent 狀態流轉時再回頭用 20 分鐘跑一次範例。
- **原文標題**：How to Build a Markov Chain in Python With NumPy
- `#機率模型` `#Python` `#NumPy`

### [Meta 讓 Cuttlefish 原生跑在 Apple Silicon Mac](https://engineering.fb.com/2026/11/13/android/cuttlefish-on-mac/)
*Engineering at Meta · 2026-11-13 · 相關度 6.2 · 存參考*

- **內容**：Meta Reality Labs 把 Android 虛擬裝置框架 Cuttlefish 與其 QEMU 後端移植到 macOS 與 Apple Silicon。
- **對你的意義**：與 LLM/Agent 轉職路線關聯低，屬於行動端工程主題。
- **今天可以做**：略過，若未來需要在 Mac 上做 Android 模擬測試再回來翻。
- **原文標題**：Cuttlefish on Mac: Running Android’s Virtual Device Framework Natively on Apple Silicon
- `#Meta` `#Android` `#虛擬化`

### [用 SimReady 素材建立機器人取放模擬](https://huggingface.co/blog/nvidia/simready-assets-robot-pick-and-place)
*Hugging Face Blog · 2026-11-13 · 相關度 5.65 · 存參考*

- **內容**：摘要資訊有限，僅從標題判斷是介紹如何用 NVIDIA SimReady 資產搭建機器人 pick-and-place 模擬場景。
- **對你的意義**：模擬環境是生成訓練資料與驗證策略的手段，概念上類似你熟悉的測試資料環境，但離 LLM 應用主線較遠。
- **今天可以做**：存入書籤，若日後碰到需要合成資料（synthetic data）的專案再深入。
- **原文標題**：Build a Robot Pick-and-Place Simulation with SimReady Assets
- `#模擬` `#機器人` `#NVIDIA` `#合成資料`

### [datasette-cluster-map 0.19 發布](https://simonwillison.net/2026/Nov/13/datasette-cluster-map/)
*Simon Willison's Weblog · 2026-11-13 · 相關度 4.83 · 存參考*

- **內容**：Datasette 老牌地圖外掛更新至 0.19，支援 Datasette 1.0a42，並改用新的 datasette-leaflet 以正確送出 referrer header。
- **對你的意義**：Datasette 是把 SQLite 資料快速變成可探索 Web 介面的工具，適合你快速做資料集 demo 或 RAG 語料檢視頁面。
- **今天可以做**：用 pip 裝 Datasette，把手上任一 CSV 轉成 SQLite 並 serve 起來看一次，約 15 分鐘。
- **原文標題**：datasette-cluster-map 0.19
- `#Datasette` `#開源工具` `#資料視覺化`

### [datasette-leaflet 0.3 發布](https://simonwillison.net/2026/Nov/13/datasette-leaflet/)
*Simon Willison's Weblog · 2026-11-13 · 相關度 4.83 · 存參考*

- **內容**：datasette-leaflet 更新至 0.3，改以 strict-origin-when-cross-origin 設定 tile 請求的 referrer policy，符合 OpenStreetMap 的使用規範。
- **對你的意義**：屬於工具相依層的小版本修正，對轉職能力沒有直接貢獻，但顯示開源維護中合規細節的重要性。
- **今天可以做**：略過，僅在使用 Datasette 地圖外掛遇到 tile 載入問題時再查。
- **原文標題**：datasette-leaflet 0.3
- `#Datasette` `#Leaflet` `#開源維護`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [4]，把 agent 的三個早期訊號（quality / cost / latency）寫成一份監控指標清單，並對照你現有 Airflow/Spark pipeline 的監控欄位，列出哪些可以直接沿用、哪些要新增（如 token 用量、輸出品質分數）。
2. 再讀 [8]，整理 Bedrock 四個影響成本的 request-level 參數（cache duration、service tier、reasoning effort、maxTokens），用一張表寫下每個參數調整後對 token 數與費率的影響，作為日後成本優化的 checklist。
3. 最後掃 [7] 與 [10]，把「cost per solved task」這個評估指標與 Natera 的 agent 架構（knowledge base → deploy → evaluation）畫成一張流程圖，標註你最缺的環節是哪一段。

---

掃描 50 篇，收錄 14 篇。來源分布：TechOrange 科技報橘 × 4、AWS Machine Learning Blog × 4、Towards Data Science × 2、Simon Willison's Weblog × 2、Engineering at Meta × 1、Hugging Face Blog × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-15 03:18 自動產生 · 摘要引擎：Claude（claude-opus-5）*