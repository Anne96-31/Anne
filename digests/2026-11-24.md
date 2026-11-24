# AI & Data 每日摘要 2026-11-24（二）

> 今天的主軸是「Agent 從實驗走向生產」：GitHub Copilot 的兆級 token 生產追蹤揭示 agent workload 與 chatbot 完全不同（LLM 呼叫與 tool 執行近 1:1），a16z 更直接提出 B2A 經濟，agent 已在建資料庫、觸發雲端部署。第二條線是「評估與維運」：Hugging Face 談 agentic evaluation、OpenAI 想把 perplexity 當成業界共同煞車線，顯示 AI Engineer 的核心價值越來越在「量測與監控」而非寫 prompt。第三條線是「基礎設施與風險」：prompt cache 命中率的統計陷阱、推論供應鏈被入侵導致 ZDR prompt 外洩、MCP 之外的輕量 tool 接法，全都是 DE 背景者最容易切入的題目。對你而言，今天最值得投資的是把資料工程的可觀測性與成本思維，平移到 agent 的 trace、eval 與 gateway 選型上。

## 🔥 今日必讀（5）

*直接補上你轉職缺的能力*

### [生產規模下的 Copilot Agent 追蹤分析](https://arxiv.org/abs/2608.00101)
*arXiv cs.LG (Machine Learning) · 2026-11-23 · 相關度 16.84 · 必讀*

- **內容**：用 740 萬使用者、57 億次 LLM 呼叫的 Copilot trace，首次刻畫 coding agent 的真實工作負載，發現它與 chatbot 截然不同：一次使用者輸入會展開成自主迴圈，LLM 呼叫與 tool 執行近 1:1。
- **對你的意義**：你熟悉 batch/streaming pipeline 的負載特性，這篇等於把同一套「workload characterization」思維搬到 agent，是你理解 agent 系統設計與成本結構最直接的橋樑。
- **今天可以做**：花 15 分鐘讀摘要與圖表，列出 3 個 agent workload 指標（turn 展開深度、LLM:tool 比例、token 放大倍數），對照你現有 pipeline 的監控欄位。
- **原文標題**：Agentic Coding in the Wild: Characterizing GitHub Copilot Traces at Production Scale
- `#Agent` `#系統設計` `#可觀測性`

### [標記零資料保留的 prompt 仍遭竊，OpenRouter 下架 3 家供應商](https://techorange.com/2026/11/23/security-ai-leaky-supply-chain/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-23 · 相關度 14.66 · 必讀*

- **內容**：Dragos 以近 200 萬筆誘餌 prompt 實測，發現多家推論供應商與轉售商外洩或記錄 prompt，連宣稱 ZDR 的請求也不保險，OpenRouter 已移除 3 家供應商與 125 個端點資格。
- **對你的意義**：AI Engineer 必須替公司做 model gateway 選型與資料治理決策，這是你從 DE 的資料合規經驗能立刻加分、也最容易被主管追問的題目。
- **今天可以做**：花 15 分鐘整理一份「LLM 供應鏈風險檢查清單」：是否走 router、ZDR 是否可驗證、敏感欄位是否在送出前遮罩。
- **原文標題**：AI 提示詞送出後誰看得到？近 200 萬筆誘餌實測：標記「零資料保留」的請求也遭竊，OpenRouter 下架 3 家推論服務供應商
- `#資安` `#LLMOps` `#Gateway`

### [90% Prompt Cache 命中率藏了什麼](https://towardsdatascience.com/what-a-90-prompt-cache-hit-rate-hides-about-attention-work/)
*Towards Data Science · 2026-11-23 · 相關度 10.78 · 必讀*

- **內容**：指出 request hit rate、token reuse 與 latency 講的是三個不同故事，引述 2026 preprint 顯示 cache 可降低 P99 但中位 TTFT 反而上升。
- **對你的意義**：這是 LLM 成本與延遲調校的核心實務，也和你在 DE 看慣的「平均值騙人、要看分位數」完全同一套直覺，容易快速上手。
- **今天可以做**：花 15 分鐘讀完，並在自己的 LLM 呼叫程式加上 TTFT 的 P50/P99 紀錄欄位。
- **原文標題**：What a 90% Prompt Cache Hit Rate Hides About Attention Work
- `#推論效能` `#成本優化` `#快取`

### [不用 MCP 的 5 種輕量 Agent 工具接法](https://www.kdnuggets.com/5-lightweight-alternatives-to-mcp-for-giving-ai-agents-tools)
*KDnuggets · 2026-11-23 · 相關度 9.74 · 必讀*

- **內容**：比較 Python dispatcher、框架內建 tools、REST adapter、subprocess 與 webhook 五種給 agent 工具的輕量方式，並說明何時才值得導入 MCP。
- **對你的意義**：讓你不被 MCP 的框架包袱卡住，先用最小程式碼搞懂 tool-calling 的本質，這是建構 Agent 系統的第一塊基本功。
- **今天可以做**：花 20 分鐘用純 Python 寫一個 function dispatcher，讓 LLM 呼叫你的一個 SQL 查詢函式並回傳結果。
- **原文標題**：5 Lightweight Alternatives to MCP for Giving AI Agents Tools
- `#Agent` `#Tool Calling` `#MCP`

### [如何建立並維護 Agentic Evaluation](https://huggingface.co/blog/agentic-evals)
*Hugging Face Blog · 2026-11-23 · 相關度 9.33 · 必讀*

- **內容**：Hugging Face 談 agent 評估體系的建立與長期維護。摘要資訊有限，僅能依標題判斷。
- **對你的意義**：評估能力是 DE 轉 AI Engineer 最大的斷層：你會做資料品質監控，但還缺一套針對多步驟 agent 行為的 eval 流程與回歸測試。
- **今天可以做**：讀完後立刻為一個 agent 任務寫 10 筆 eval 案例（輸入、期望工具呼叫、通過判準），存成 JSONL。
- **原文標題**：How to build and maintain an agentic evaluation
- `#評估` `#LLMOps` `#Agent`

## 👀 值得快速瀏覽（5）

*掃過標題與重點即可*

### [Spark Structured Streaming 原生 Lakebase Postgres Sink GA](https://www.databricks.com/blog/announcing-general-availability-native-lakebase-postgres-sink-spark-structured-streaming)
*Databricks Blog · 2026-11-23 · 相關度 14.78 · 快速瀏覽*

- **內容**：Databricks 宣布 Spark Structured Streaming 可原生寫入 Lakebase Postgres，鎖定詐欺偵測、即時個人化等低延遲場景。摘要資訊有限。
- **對你的意義**：這正是你既有技能的延伸：低延遲 feature serving 是 RAG/Agent 線上特徵與 context 供給的基礎，DE 背景在此有天然優勢。
- **今天可以做**：花 10 分鐘讀官方文件，寫下「若我的 RAG 要即時取用使用者最新行為特徵，這個 sink 會放在架構的哪一層」。
- **原文標題**：Announcing General Availability of native Lakebase Postgres sink for Spark Structured Streaming
- `#資料工程` `#Streaming` `#Feature Serving`

### [a16z 提 B2A 經濟：Agent 開始建資料庫與觸發部署](https://techorange.com/2026/11/23/a16z-welcome-b2a-economy/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-23 · 相關度 14.18 · 快速瀏覽*

- **內容**：a16z 主張 AI agent 正成為企業的新客戶，並以 Supabase、Stripe、Vercel 數據說明 agent 已在實際建資料庫、呼叫 API 與部署雲端；但 PPC Land 指出部分說法超出其圖表數據。
- **對你的意義**：這預示「給 agent 用的介面」會成為新職責：你未來可能要設計讓 agent 安全存取的 API/資料層，這正是 DE 的強項延伸。
- **今天可以做**：花 10 分鐘思考並寫下：若要讓 agent 安全查詢你現有的資料倉儲，需要哪 3 道護欄（權限範圍、查詢白名單、成本上限）。
- **原文標題**：a16z 提 B2A 經濟：AI 代理的生意不只在購物車，連資料庫、雲端部署都開始用 AI
- `#Agent` `#產業趨勢` `#API 設計`

### [OpenAI 公開困惑度數據，想替業界訂煞車線](https://techorange.com/2026/11/23/openai-perplexity-common-limits/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-23 · 相關度 14.0 · 快速瀏覽*

- **內容**：OpenAI 首席科學家公開歷代模型 perplexity 數據，提議前沿業者以此與其他指標訂共同開發上限，並呼籲建立共享評估與紅隊規範。
- **對你的意義**：幫你釐清 perplexity 這類 pretraining 指標與你實際要做的 task-level eval 的差別，避免誤用錯的量尺評估 LLM 應用。
- **今天可以做**：花 10 分鐘寫一張對照表：perplexity vs. task accuracy vs. LLM-as-judge，各自量到什麼、量不到什麼。
- **原文標題**：OpenAI 公開內部「困惑度」數據，想替業界訂「煞車線」：這把量尺能成為共同標準嗎？
- `#評估` `#模型基礎` `#AI 治理`

### [GLM-5.4 與 Loop Transformer 架構](https://simonwillison.net/2026/Nov/23/glm-54/)
*Simon Willison's Weblog · 2026-11-23 · 相關度 7.76 · 快速瀏覽*

- **內容**：Z.ai 發表 GLM-5.4，首次採用 looped transformer：共享權重的層組多次迭代，在不增加參數量下取得更深網路；一週內已是第二個採此架構的模型。
- **對你的意義**：幫你建立「架構選擇如何影響推論延遲與成本」的判斷力，這是選模型時除了 benchmark 之外更深一層的依據。
- **今天可以做**：花 10 分鐘讀完並筆記 looped transformer 的一句話定義，以及它對推論延遲可能的影響。
- **原文標題**：GLM-5.4: Toward Generalized Coding with Our First Loop Transformer
- `#模型架構` `#開源模型` `#Coding Model`

### [用生日悖論測小型 LLM 的輸出多樣性](https://towardsdatascience.com/the-birthday-paradox-shows-small-llms-pick-from-about-6-of-40-words/)
*Towards Data Science · 2026-11-23 · 相關度 6.12 · 快速瀏覽*

- **內容**：同一問題問 300 次、數重複次數，再用生日悖論反推模型實際的有效候選詞數量，發現小型 LLM 大約只從 40 個詞中選 6 個。
- **對你的意義**：提供一個幾行 Python 就能跑的輸出多樣性量測法，正好補上你對 LLM 非決定性行為的量化直覺，對設計 eval 很有用。
- **今天可以做**：花 15 分鐘照文中方法，對你手上的模型跑 100 次同一 prompt，統計重複率。
- **原文標題**：The Birthday Paradox Shows Small LLMs Pick From About 6 of 40 Words
- `#評估` `#取樣` `#實驗方法`

## 🗂️ 存起來參考（4）

*之後需要時再回頭看*

### [AI 代理設計全新 CPU 架構 Frostbite](https://techorange.com/2026/11/23/architect-labs-ai-cpu-frostbite/?utm_source=rss&utm_medium=feed&utm_campaign=techorange_rss)
*TechOrange 科技報橘 · 2026-11-23 · 相關度 12.95 · 存參考*

- **內容**：新創 Architect Labs 宣稱其 AI 系統自主設計出採用 interaction nets 的全新指令集 CPU，流片前模擬每瓦效能達傳統循序核心 4.59 倍。
- **對你的意義**：屬於 agent 應用於硬體設計的前沿案例，對日常轉職工作幫助有限，但可作為「agent 能走多遠」的認知素材。
- **今天可以做**：花 5 分鐘掃過，記下「流片前模擬數據 ≠ 實機驗證」這個評估陷阱即可。
- **原文標題**：AI 代理從零設計全新 CPU 架構「Frostbite」！Architect Labs 宣稱流片前模擬每瓦效能達循序核心 4.59 倍
- `#硬體` `#Agent` `#前沿研究`

### [2026 年用 AI 工具更快學資料科學](https://www.kdnuggets.com/how-to-use-ai-tools-to-learn-data-science-faster-in-2026)
*KDnuggets · 2026-11-23 · 相關度 10.01 · 存參考*

- **內容**：介紹如何組合 AI 助理、coding 工具與自適應學習平台來縮短學習曲線。偏入門導向，摘要資訊有限。
- **對你的意義**：對已有 DE 實戰經驗的你新意不多，但可挑其中的學習工作流技巧，加速你補 LLM 領域知識的速度。
- **今天可以做**：花 5 分鐘掃標題與小標，挑 1 個學習工作流技巧套用到今天的讀論文流程。
- **原文標題**：How to Use AI Tools to Learn Data Science Faster in 2026
- `#學習方法` `#職涯`

### [Ladybird 瀏覽器首個 alpha 釋出](https://simonwillison.net/2026/Nov/23/ladybird/)
*Simon Willison's Weblog · 2026-11-23 · 相關度 6.0 · 存參考*

- **內容**：從零實作 HTML、CSS、JS 與 WebAssembly 的獨立瀏覽器 Ladybird 發布首個 alpha，macOS/Linux 可直接安裝。
- **對你的意義**：與 AI Engineer 轉職路徑關聯低，純屬開源生態觀察，可作為 agent 瀏覽器環境的潛在備選知識。
- **今天可以做**：花 3 分鐘掃過，有興趣再收藏即可。
- **原文標題**：Ladybird's first alpha release
- `#開源` `#瀏覽器`

### [datasette-charts 0.1a0 發布](https://simonwillison.net/2026/Nov/23/datasette-charts/)
*Simon Willison's Weblog · 2026-11-23 · 相關度 5.69 · 存參考*

- **內容**：Simon Willison 用 LLM 快速做出原型，推出可對任意 Datasette 表或 SQL 查詢自動建議圖表類型的視覺化外掛。
- **對你的意義**：是「資料工具 + LLM 輔助開發」的具體示範，值得學他如何用 heuristics 自動推薦，而不是全交給模型亂猜。
- **今天可以做**：花 10 分鐘在 Datasette Lite 試玩一次，記下它用什麼欄位型別 heuristics 來推薦圖表。
- **原文標題**：datasette-charts 0.1a0
- `#工具` `#資料視覺化` `#開源`

## 🎯 今天的 30 分鐘學習計畫

1. 先讀 [10] agentic evaluation，動手把自己想做的一個 agent 任務寫成 10 筆 eval dataset（輸入、期望行為、判定準則），這是 DE→AI Engineer 最關鍵的能力缺口。
2. 讀 [9]，用純 Python function dispatcher 做一個最小 tool-calling 範例（不裝 MCP server），確認自己能從零接通 LLM 與工具。
3. 掃 [1] 與 [7]，把 agent workload 的特性（LLM call 與 tool 1:1、cache hit rate 與 TTFT 的落差）寫成一頁筆記，對照你現有 pipeline 的監控指標設計。

---

掃描 342 篇，收錄 14 篇。來源分布：TechOrange 科技報橘 × 4、Simon Willison's Weblog × 3、Towards Data Science × 2、KDnuggets × 2、arXiv cs.LG (Machine Learning) × 1、Databricks Blog × 1、Hugging Face Blog × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-24 09:45 自動產生 · 摘要引擎：Claude（claude-opus-5）*