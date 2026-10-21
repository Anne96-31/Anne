# AI & Data 每日摘要 2026-10-22（四）

> 今天的主軸是「Agent 工具治理」與「推論基礎設施開源化」兩條線：AWS 連發 Agent Registry 與 Bedrock AgentCore MCP Gateway，顯示 agent 的工具管理正從硬編碼走向 runtime 語意搜尋與集中式認證閘道——這和 DE 熟悉的 schema registry / 連線憑證治理高度同構，是你最容易遷移既有經驗的切入點。另一條線是 DeepSeek 開源 DeepInfer 推論引擎、AWS Trainium 上的 Difflet 與 linear attention 模型，推論成本與記憶體（KV cache）成為系統設計的核心變數。此外 fine-tuning（SFT vs GRPO）有了可量化的決策案例，而 TDS 的 dbt snapshot pipeline 與非同步模擬平台兩篇則提醒：AI Engineer 的底層仍是扎實的資料與工作流工程。建議今天把重心放在 MCP/Agent Registry 的概念與一個可跑的最小範例。

## 🔥 今日必讀（6）

*直接補上你轉職缺的能力*

### [DeepSeek 開源推論框架 DeepInfer](https://techorange.com/2026/10/21/deepseek-deepinfer-ai/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-10-21 · 相關度 14.52 · 必讀*

- **內容**：DeepSeek 開源整合式推論引擎 DeepInfer，公開支撐單叢集日處理 155 兆 tokens 的平行運算、非同步排程與 speculative decoding 設計。
- **對你的意義**：AI Engineer 必須懂推論成本結構；從開放權重到開放推論引擎，意味著自建部署的門檻下降，你需要理解 batching、排程與解碼優化這些「服務層」概念。
- **今天可以做**：查閱並筆記三個名詞：continuous batching、speculative decoding、MoE expert parallelism，各用兩句話寫出它們各自省下什麼資源。
- **原文標題**：DeepSeek 把 AI 推論框架開源了！揭露單一叢集日處理 155 兆 Tokens 的系統設計
- `#推論引擎` `#開源` `#DeepSeek` `#部署效能`

### [我做了一條追蹤目標職缺市場的 pipeline](https://towardsdatascience.com/i-built-a-pipeline-to-track-the-job-market-im-trying-to-break-into/)
*Towards Data Science · 2026-10-21 · 相關度 11.2 · 必讀*

- **內容**：作者用 dbt snapshots 建增量 pipeline 追蹤職缺資料，並分享途中遇到 API 回傳不實資料的踩坑經驗。
- **對你的意義**：用你最熟的 DE 技能打造轉職用的個人專案，既練手也是作品集；之後再加上 embedding 做職缺語意搜尋就能延伸成 AI 專案。
- **今天可以做**：今天建一個最小版本：抓 20 筆 AI Engineer 職缺存成 table，規劃好 snapshot 欄位（SCD2）與後續要加的 JD embedding 欄位。
- **原文標題**：I Built a Pipeline to Track the Job Market I'm Trying to Break Into.
- `#dbt` `#資料管線` `#作品集` `#職涯`

### [在 SageMaker HyperPod 上微調 GPT-OSS-20B](https://aws.amazon.com/blogs/machine-learning/fine-tuning-gpt-oss-20b-for-multilingual-reasoning-on-amazon-sagemaker-hyperpod/)
*AWS Machine Learning Blog · 2026-10-20 · 相關度 10.25 · 必讀*

- **內容**：實作分享 GPT-OSS-20B 多語推理微調，SFT 把推理語言正確率從 22% 拉到 100%，GRPO 在還有空間處再加分，並給出 SFT 與 RL 的選擇準則。
- **對你的意義**：fine-tuning 的「何時該做、該用哪種」是 AI Engineer 面試與實務的高頻題，這篇提供有量化結果的決策依據。
- **今天可以做**：做一張決策表：問題屬於格式/風格不一致→SFT；屬於偏好與多解排序→RL/GRPO；屬於知識缺口→RAG，各寫一個例子。
- **原文標題**：Fine-tuning GPT-OSS-20B for multilingual reasoning on Amazon SageMaker HyperPod
- `#fine-tuning` `#SFT` `#GRPO` `#模型評估`

### [用 AWS Agent Registry 在 runtime 發現工具](https://aws.amazon.com/blogs/machine-learning/discover-tools-at-runtime-with-aws-agent-registry/)
*AWS Machine Learning Blog · 2026-10-20 · 相關度 9.54 · 必讀*

- **內容**：當 agent 工具從數個長到數百個，硬編碼 wiring 會崩潰；本文示範以語意搜尋在 runtime 發現 MCP server 與 A2A agent 的 Discover-Instantiate-Execute 迴圈。
- **對你的意義**：這是 agent 系統的規模化核心問題，概念上等同你熟悉的 metadata catalog / schema registry，是 DE 轉 AI 最可直接遷移經驗的題目。
- **今天可以做**：畫出 Discover-Instantiate-Execute 流程圖，並寫下它與 Airflow plugin 註冊機制的三個差異點。
- **原文標題**：Discover tools at runtime with AWS Agent Registry
- `#AI Agent` `#MCP` `#工具治理` `#AWS`

### [Eon 用 Bedrock AgentCore MCP Gateway 做多雲調查](https://aws.amazon.com/blogs/machine-learning/how-eon-built-multi-cloud-investigation-with-an-mcp-gateway-on-amazon-bedrock-agentcore/)
*AWS Machine Learning Blog · 2026-10-20 · 相關度 9.03 · 必讀*

- **內容**：Eon 以單一認證 gateway 取代 AWS/GCP/Azure 各自的工具憑證與本機 MCP process，讓逾百位開發者與 agent 共用存取，新人上手從兩天縮到兩分鐘。
- **對你的意義**：展示 agent 在企業環境的身分認證與權限治理實務，正是 DE 熟悉的連線管理延伸，也是上線維運能力的加分項。
- **今天可以做**：列出你現有 pipeline 中散落的三組憑證，設計一個「統一 gateway + 最小權限」的改法草圖。
- **原文標題**：How Eon built multi-cloud investigation with an MCP Gateway on Amazon Bedrock AgentCore
- `#MCP Gateway` `#Bedrock AgentCore` `#安全治理` `#企業案例`

### [用 Scikit-LLM 做命名實體辨識](https://www.kdnuggets.com/named-entity-recognition-using-scikit-llm)
*KDnuggets · 2026-10-21 · 相關度 5.0 · 必讀*

- **內容**：示範用 Scikit-LLM 以 scikit-learn 風格 API 建立客製化 NER pipeline，靠 LLM 推理能力取代傳統標註訓練。
- **對你的意義**：對 DE 很實用：非結構化文字（工單、log、合約）轉結構化欄位是你 pipeline 的常見需求，這是低成本把 LLM 嵌入 ETL 的做法。
- **今天可以做**：用 Scikit-LLM 跑一個最小範例，拿 10 筆你熟悉的業務文字抽出 3 個實體欄位，記錄準確度與 token 成本。
- **原文標題**：Named Entity Recognition Using Scikit-LLM
- `#NER` `#Scikit-LLM` `#非結構化資料` `#ETL`

## 👀 值得快速瀏覽（5）

*掃過標題與重點即可*

### [明昌國際導入台達 DIAEMS 設備管理系統](https://techorange.com/2026/10/21/delta-diaems/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-10-21 · 相關度 14.92 · 快速瀏覽*

- **內容**：傳統金屬加工廠把紙本設備維護紀錄數位化，解決非計畫停機、庫存失控與老師傅經驗難傳承的問題。
- **對你的意義**：這是典型「有資料但沒結構化」的場域，正是 DE 背景切入 AI 落地案的優勢起點：先有設備事件資料管線，之後才談維修知識庫 RAG。
- **今天可以做**：花 10 分鐘構想：若要把這類維修工單與技師經驗做成 RAG 知識庫，資料來源、chunking 策略與 metadata 欄位各該怎麼設計，寫成半頁筆記。
- **原文標題**：金屬加工大廠明昌國際攜手台達加速數位轉型，導入設備管理系統 DIAEMS
- `#製造業 AI` `#資料數位化` `#台灣案例`

### [Trainium2 上訓練與服務 Laplace 3B linear attention 模型](https://aws.amazon.com/blogs/machine-learning/beyond-the-kv-cache-training-and-serving-i14s-laplace-3b-linear-attention-model-on-aws-trainium2-with-native-pytorch/)
*AWS Machine Learning Blog · 2026-10-20 · 相關度 12.87 · 快速瀏覽*

- **內容**：i14 用原生 PyTorch 在 Trainium2 訓練 linear attention 模型，其 recurrent state 固定 29.5 MB，不隨 context 長度成長，避開 KV cache 膨脹。
- **對你的意義**：長 context 的記憶體成本是 LLM 服務容量規劃的核心變數，理解 KV cache 為何成長，才有能力估算 GPU 需求與併發上限。
- **今天可以做**：用紙筆推算一次：transformer KV cache 大小公式（層數×頭數×維度×context×2×精度），套一個 7B 模型與 32k context 算出數字。
- **原文標題**：Beyond the KV cache: Training and serving i14’s Laplace 3B linear attention model on AWS Trainium2 with native PyTorch
- `#KV cache` `#linear attention` `#推論記憶體`

### [5 個最佳 AI Agent Skills GitHub 專案](https://www.kdnuggets.com/5-best-github-repositories-for-ai-agent-skills)
*KDnuggets · 2026-10-21 · 相關度 12.6 · 快速瀏覽*

- **內容**：整理五個熱門 agent skill 集合，協助 coding agent 進行規劃、測試、除錯、review 與軟體建構。摘要資訊有限，細節需看原文。
- **對你的意義**：直接提供可抄的 agent 能力設計樣板，對剛要從 pipeline 思維轉成 agent 思維的你，是最省時的入門素材庫。
- **今天可以做**：打開其中一個 repo，挑一個 skill 的 prompt/工具定義讀完，模仿它寫一個「SQL 查詢檢查」skill 的定義草稿。
- **原文標題**：5 Best GitHub Repositories for AI Agent Skills
- `#AI Agent` `#開源` `#GitHub` `#學習資源`

### [OpenAI 如何打造 ChatGPT 的廣告技術堆疊](https://openai.com/index/building-chatgpt-ad-stack)
*OpenAI News · 2026-10-21 · 相關度 12.45 · 快速瀏覽*

- **內容**：OpenAI 說明以 LLM 理解對話意圖、將廣告與回答明確區隔，並在規模下維持相關性的廣告系統設計。
- **對你的意義**：是少見的 LLM 產品級系統設計公開文，可觀察他們如何做意圖抽取、排序與信任邊界——這些都是 AI Engineer 的系統設計考題。
- **今天可以做**：讀完後寫下他們「讓廣告與答案分離」的三個機制，思考同樣手法能否用在你的 RAG 系統區隔「來源內容」與「模型臆測」。
- **原文標題**：How we built ChatGPT’s novel ad stack for user trust and relevance
- `#系統設計` `#OpenAI` `#LLM 產品`

### [把長時間 Python 模擬變成自助服務平台](https://towardsdatascience.com/how-to-turn-long-running-python-simulations-into-a-self-service-platform/)
*Towards Data Science · 2026-10-21 · 相關度 8.9 · 快速瀏覽*

- **內容**：作者分享在 AWS 上建非同步工作負載的經驗，聚焦 queue 設計、失敗復原與可重現性。
- **對你的意義**：LLM 的批次推論、評估跑分與 fine-tuning job 都是長時任務，這套 queue 與 retry 設計可直接套用到 AI workload 平台。
- **今天可以做**：對照你現在的 Airflow DAG，寫下三個讓 LLM 批次評估任務具備可重現性的要素（seed、版本鎖定、輸入快照）。
- **原文標題**：How to Turn Long-Running Python Simulations Into a Self-Service Platform
- `#非同步架構` `#平台工程` `#可重現性`

## 🗂️ 存起來參考（3）

*之後需要時再回頭看*

### [Difflet：AWS Trainium 上的 Diffusion 推論引擎](https://arxiv.org/abs/2610.23047)
*arXiv cs.LG (Machine Learning) · 2026-10-21 · 相關度 13.43 · 存參考*

- **內容**：論文提出 Difflet，讓五種 diffusion pipeline 共用一套編譯後端，並在每個去噪步驟由 host controller 決定是否重用快取輸出。
- **對你的意義**：展示「用 runtime 決策省運算」的系統思維，與你在 pipeline 做增量處理/快取的直覺相通，但應用在模型服務層。
- **今天可以做**：只讀 abstract，記下「step-level caching 決策」這個模式，想一個你自家 pipeline 中可類比的重算略過機制。
- **原文標題**：DIFFLET: A Fast Inference Engine for Diffusion Transformer Models on AWS Trainium
- `#diffusion` `#Trainium` `#推論優化` `#論文`

### [Google Coral NPU 擴大商用，瞄準智慧眼鏡](https://techorange.com/2026/10/21/unifying-edge-ai-coral-npus-open-standard-brings-portable-energy-viable-intelligence-model-silicon/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-10-21 · 相關度 10.27 · 存參考*

- **內容**：Synaptics 推出整合開源 Coral NPU 的 Astra SR200 處理器，讓智慧眼鏡、攝影機等裝置能離線執行 Gemma 等模型。
- **對你的意義**：edge AI 代表未來一部分推論會離開雲端，對資料流設計與模型量化需求不同；屬於擴大視野、短期非核心。
- **今天可以做**：略讀標題與重點即可，記下「RISC-V + Apache 2.0 開源 NPU」這個趨勢關鍵字。
- **原文標題**：Google 免授權費 Coral NPU 擴大商用：新思國際推最高 400 GOPS 晶片瞄準智慧眼鏡
- `#edge AI` `#NPU` `#硬體趨勢`

### [10 個付費軟體的免費開源替代方案](https://www.analyticsvidhya.com/blog/2026/10/open-source-alternatives-paid-software/)
*Analytics Vidhya · 2026-10-21 · 相關度 6.93 · 存參考*

- **內容**：整理十款可取代付費軟體的開源工具，涵蓋影像編輯、專案管理、文件簽署等。與 AI 工程核心關聯低。
- **對你的意義**：與 DE 轉 AI Engineer 的能力落差關聯不大，僅屬生產力工具資訊。
- **今天可以做**：今天可略過，若有軟體訂閱成本困擾再回頭看清單。
- **原文標題**：10 Free Open Source Alternatives to Paid Software
- `#開源工具` `#生產力`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [10] AWS Agent Registry 的 Discover-Instantiate-Execute 迴圈，用 15 分鐘畫一張圖，對照你熟悉的 Airflow Operator 註冊 / schema registry，寫下「工具發現」與「metadata catalog」的相同與不同點。
2. 接著讀 [11] Eon 的 MCP Gateway 案例，列出 3 個你現在 pipeline 中的憑證管理痛點，思考若改成單一認證閘道暴露給 agent 會怎麼設計。
3. 最後花 10 分鐘掃 [9] SFT vs GRPO 的決策準則，做一張「什麼情況選 prompt engineering / RAG / SFT / RL」的決策筆記，當作日後專案的判斷依據。

---

掃描 502 篇，收錄 14 篇。來源分布：AWS Machine Learning Blog × 4、TechOrange 科技報橘 × 3、KDnuggets × 2、Towards Data Science × 2、arXiv cs.LG (Machine Learning) × 1、OpenAI News × 1、Analytics Vidhya × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-10-22 02:46 自動產生 · 摘要引擎：Claude（claude-opus-5）*