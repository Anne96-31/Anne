# AI & Data 每日摘要 2026-11-28（六）

> 今天的主軸集中在「Agent 的工程化」：Code Mode 與 tool calling 的成本/延遲取捨（16 個工具是分水嶺）、speculative decoding 對 agent loop 反而需要搭配 cache、以及用 Opik 做 agent 的可觀測性與自我修正——三者合起來就是 AI Engineer 最核心的「評估 + 效能 + 除錯」能力組。基礎建設面則有 llama.cpp 在 AMD 上的 benchmark dashboard 與 Trainium3 推論實測，顯示推論硬體選型正在多元化，對成本控管思維的 DE 很友善。產業面，美國算力與反蒸餾管制壓縮中國模型進度、7-Eleven 把 AI 落地到招募與門市流程、小鵬人形機器人走商用先行路線，說明 AI 價值最終還是落在資料整合與流程自動化上。另外 Simon Willison 幾則引用則提醒：生成內容的同質化與真實性治理，將成為上線系統必須面對的議題。

## 🔥 今日必讀（3）

*直接補上你轉職缺的能力*

### [Code Mode vs Tool Calling：16 工具是交叉點](https://towardsdatascience.com/code-mode-vs-tool-calling-benchmarks-find-a-16-tool-crossover/)
*Towards Data Science · 2026-11-27 · 相關度 10.44 · 必讀*

- **內容**：實測顯示在 100 筆 fan-out 任務上 Code Mode 比 tool calling 便宜 120 倍、快 18 倍，但單一查詢時可靠度較差，約在 16 個工具處出現交叉點。
- **對你的意義**：這是 agent 架構選型的硬數據，直接補上你缺的「如何設計 agent 執行層」能力；fan-out 批次優於逐次呼叫的直覺，和你熟悉的 batch vs row-by-row 完全同源。
- **今天可以做**：讀完後寫下一條自己的決策規則：工具數 / 任務筆數達到什麼條件時改用 Code Mode。
- **原文標題**：Code Mode vs. Tool Calling Benchmarks Find a 16-Tool Crossover
- `#Agent` `#MCP` `#成本優化`

### [用 Opik 打造會自我修正的 AI Agent](https://www.analyticsvidhya.com/blog/2026/11/self-correcting-ai-agents-opik/)
*Analytics Vidhya · 2026-11-27 · 相關度 8.8 · 必讀*

- **內容**：探討 agent 在真實用戶下常見失敗（選錯工具、忽略檢索內容），並用 Opik 的 observability 與評估能力找出原因並修正。
- **對你的意義**：LLMOps 是 DE 最容易遷移也最吃香的切入點；trace + metric + 回饋修正，本質就是你做資料品質監控的 LLM 版。
- **今天可以做**：今天 pip install opik，對一個最小 agent 加上 trace 與一個 hallucination/相關性 metric 跑一次。
- **原文標題**：Building Self-Correcting AI Agents with Opik
- `#LLMOps` `#可觀測性` `#Agent評估`

### [Speculative Decoding 加速工具呼叫，但 Agent 需要快取](https://towardsdatascience.com/speculative-decoding-makes-tool-calls-faster-agents-need-a-cache/)
*Towards Data Science · 2026-11-27 · 相關度 6.12 · 必讀*

- **內容**：以 Qwen3 與 Llama 在 llama.cpp 實測，draft model 讓程式碼、JSON、tool call 生成最多快 1.7 倍，但未加 cache 的 agent loop 反而慢 6%。
- **對你的意義**：補上 AI Engineer 必備的推論效能直覺：知道加速技巧有適用邊界，且 cache 設計決定端到端延遲，這正是上線維運會被追問的點。
- **今天可以做**：把 speculative decoding 與 prompt/KV cache 的關係畫成一張流程草圖，標出 agent loop 的瓶頸在哪。
- **原文標題**：Speculative Decoding Makes Tool Calls Faster. Agents Need a Cache.
- `#推論優化` `#llama.cpp` `#快取`

## 👀 值得快速瀏覽（4）

*掃過標題與重點即可*

### [7-Eleven 用 AI 改造招募、結帳與維修](https://techorange.com/2026/11/27/7-eleven-ai-data-automation-convenience/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-27 · 相關度 15.03 · 快速瀏覽*

- **內容**：美國 7-Eleven 以電腦視覺、LLM 與資料整合改造門市結帳、跨通路服務與後勤營運，招募週期從 10 天縮到 3 天內。
- **對你的意義**：這是典型「資料整合 + AI 落地」案例，DE 的 pipeline 能力正是這類專案的地基；可用來建立你在面試時談業務價值（週期縮短、尖峰人力）的敘事框架。
- **今天可以做**：花 10 分鐘列出文中提到的 3 個 AI 應用場景，各寫一句它背後需要哪些資料來源與管線。
- **原文標題**：美國 7-Eleven 把 AI 用進招募、結帳到設備維修，招人時間從 10 天縮到不到 3 天
- `#產業案例` `#零售` `#資料整合`

### [美國算力管制與反蒸餾夾擊中國模型](https://techorange.com/2026/11/27/us-curbs-delay-china-ai/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-27 · 相關度 13.27 · 快速瀏覽*

- **內容**：BIS 新規把算力管制延伸到海外資料中心，加上 OpenAI/Anthropic 收緊反蒸餾，傳智譜 GLM-5.5、月之暗面進度受阻。
- **對你的意義**：提醒 AI Engineer 在選型時要考量模型供應鏈與地緣風險，並理解 distillation 作為壓縮成本的技術手段與其法律邊界。
- **今天可以做**：用 5 分鐘查一下 model distillation 的基本定義與用途，寫 3 行筆記區分它與 fine-tuning。
- **原文標題**：美國算力管制與反蒸餾雙重夾擊：傳中國 AI 旗艦模型恐延宕，月之暗面取消印尼交易轉向歐洲租算力
- `#地緣政治` `#算力` `#distillation`

### [用 Scikit-LLM 做非監督分群與主題探索](https://www.kdnuggets.com/blending-unsupervised-clustering-tasks-with-scikit-llm)
*KDnuggets · 2026-11-27 · 相關度 5.77 · 快速瀏覽*

- **內容**：示範一個兩階段 pipeline：先做文件分群，再用 LLM 的摘要能力做主題發現。
- **對你的意義**：這是把 embedding 與 LLM 嵌入既有資料處理流程的實用樣板，離 DE 日常最近，可直接套到你現有的文本資料表。
- **今天可以做**：用自己手邊一份文字資料（如 log 或工單）跑一次 embedding + KMeans，再讓 LLM 幫每群命名。
- **原文標題**：Blending Unsupervised Clustering Tasks with Scikit-LLM
- `#embedding` `#clustering` `#資料管線`

### [引用 Jack Despain Zhou：AI 造成去個體化](https://simonwillison.net/2026/Nov/26/jack-despain-zhou/)
*Simon Willison's Weblog · 2026-11-26 · 相關度 3.88 · 快速瀏覽*

- **內容**：評論指出 AI 生成內容讓影片、簡報、郵件都「聽起來像 Claude」，產生嚴重的風格同質化。
- **對你的意義**：提醒在設計 LLM 產品時要處理輸出風格與可信度，也關係到你未來要設計的人味與品質評估指標。
- **今天可以做**：花 3 分鐘讀完，想一個可量化「輸出是否過於模板化」的評估指標。
- **原文標題**：Quoting Jack Despain Zhou
- `#AI倫理` `#內容品質` `#觀點`

## 🗂️ 存起來參考（6）

*之後需要時再回頭看*

### [小鵬人形機器人明年量產，先當門市店員](https://techorange.com/2026/11/27/xpeng-iron-humanoid-household-chores-china-gap/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-27 · 相關度 11.67 · 存參考*

- **內容**：小鵬 IRON 機器人將於 2027 年量產並先在門市受訓，採三層 AI 架構與自研晶片，家用部署還要再等 1～2 年。
- **對你的意義**：對 LLM 應用轉職者而言關聯較弱，但可觀察「商用場域先行、累積真實資料再擴張」的落地節奏，與 RAG/Agent 產品上線策略邏輯相通。
- **今天可以做**：掃標題與時程段落即可，記下「商用先行收資料」這個產品策略一句話。
- **原文標題**：小鵬人形機器人明年量產、先當門市店員，顧宏地：商用站穩後 1～2 年才考慮進家庭
- `#機器人` `#physical AI` `#產業動態`

### [10 個學 AI 決策模型的 GitHub 專案](https://www.kdnuggets.com/10-github-repositories-to-master-ai-decision-models)
*KDnuggets · 2026-11-27 · 相關度 8.69 · 存參考*

- **內容**：整理 10 個涵蓋建模、訓練、fine-tuning、部署與評估 AI 決策模型的開源 repo。
- **對你的意義**：可當作補齊模型生命週期實作經驗的練習清單，適合挑一兩個做成自己的作品集專案。
- **今天可以做**：挑 1 個 repo clone 下來跑通 README 的 quickstart，記錄遇到的環境問題。
- **原文標題**：10 GitHub Repositories to Master AI Decision Models
- `#開源` `#學習資源` `#作品集`

### [用 Trainium3 與 LTX-2.5 生成影片](https://huggingface.co/blog/video-trainium3)
*Hugging Face Blog · 2026-11-27 · 相關度 4.2 · 存參考*

- **內容**：摘要資訊有限：依標題判斷為在 AWS Trainium3 晶片上執行 LTX-2.5 影片生成模型的實測分享。
- **對你的意義**：了解 GPU 以外的加速器選項，對日後評估推論成本與雲端選型有參考價值，但非當前轉職核心。
- **今天可以做**：存入書籤，日後評估非 NVIDIA 推論方案時再讀。
- **原文標題**：Taking Trainium3 to the Track: Generating Videos with LTX-2.5
- `#Trainium` `#影片生成` `#硬體`

### [llama.cpp 推出 AMD Ryzen/Radeon benchmark 儀表板](https://huggingface.co/blog/ggml-org/llamacpp-amd-bench)
*Hugging Face Blog · 2026-11-26 · 相關度 3.73 · 存參考*

- **內容**：摘要資訊有限：依標題判斷為 ggml 團隊釋出針對 AMD 硬體的 llama.cpp 效能 benchmark 儀表板。
- **對你的意義**：本地端推論選型與成本評估是 AI Engineer 常見任務，這類 benchmark 可作為硬體決策的客觀依據。
- **今天可以做**：打開儀表板掃一眼，記下一個你熟悉模型在消費級硬體的 tokens/s 量級。
- **原文標題**：Introducing the llama.cpp benchmark dashboard for AMD Ryzen and Radeon
- `#llama.cpp` `#benchmark` `#本地推論`

### [NYT 警告攝影師勿更新含 AI 功能的 Photoshop](https://simonwillison.net/2026/Nov/26/hn-50651685/)
*Simon Willison's Weblog · 2026-11-26 · 相關度 3.46 · 存參考*

- **內容**：Simon Willison 分享 NYT 對新聞照片不得 AI 修圖的立場，強調照片必須呈現拍攝原貌。
- **對你的意義**：是「生成式 AI 與內容真實性治理」的實例，未來你在企業導入 AI 時會遇到類似的合規與政策界線問題。
- **今天可以做**：讀完後寫一句話：若你的 RAG 系統要標示「AI 生成/人工內容」，技術上要存哪些 metadata。
- **原文標題**：The New York Times warns photographers not to update Photoshop over AI features
- `#內容真實性` `#合規` `#媒體`

### [引用 Scott Aaronson：AI 開啟數學新大陸](https://simonwillison.net/2026/Nov/25/scott-aaronson/)
*Simon Willison's Weblog · 2026-11-25 · 相關度 3.23 · 存參考*

- **內容**：Aaronson 以顯微鏡與望遠鏡比喻，形容 AI 讓複雜度理論與數學真理的解析度大幅提升。
- **對你的意義**：屬於視野拓展型內容，與日常 AI Engineer 工程任務關聯不大。
- **今天可以做**：當成 3 分鐘的閱讀休息，不需額外行動。
- **原文標題**：Quoting Scott Aaronson
- `#觀點` `#研究` `#數學`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [4] Code Mode vs Tool Calling，用自己手上的一個 Airflow/ETL 任務想像：若改成 agent，工具數量會是多少？寫下何時該走 Code Mode 的判斷規則（10 分鐘）。
2. 裝一次 Opik（[5]），對一個最小 RAG 或 tool-calling agent 加上 trace 與一條 evaluation metric，體驗「可觀測性 → 自動修正」的閉環（15 分鐘）。
3. 掃過 [7] 的 speculative decoding 結論，把『draft model + cache』整理成一頁推論成本筆記，對照你熟悉的批次 vs 串流管線優化直覺（5 分鐘）。

---

掃描 40 篇，收錄 13 篇。來源分布：TechOrange 科技報橘 × 3、Simon Willison's Weblog × 3、Towards Data Science × 2、KDnuggets × 2、Hugging Face Blog × 2、Analytics Vidhya × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-28 06:47 自動產生 · 摘要引擎：Claude（claude-opus-5）*