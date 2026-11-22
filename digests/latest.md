# AI & Data 每日摘要 2026-11-23（一）

> 今天這批文章的主軸有三條：一是 LLM 基礎理解（positional embeddings、perplexity 作為評估指標），這正是 DE 轉 AI Engineer 最常被問、也最容易跳過的底層知識；二是 agent 化的工作流平台（AWS Quick 的多 agent 協作、flows、Meta ads connector），顯示「資料源 + 連接器 + agent 編排」正在變成新一代的 pipeline 形態，DE 的既有技能可以直接平移；三是 AI 時代的角色升級（TDS 談四類分析、Simon Späti 的寫作訪談），共同訊號是：把 AI agent 當成初階隊友，自己往問題定義、評估與業務溝通的抽象層往上走。整體而言，今日最值得投資的是「評估能力」與「agent 編排心智模型」。

## 🔥 今日必讀（3）

*直接補上你轉職缺的能力*

### [位置編碼解析：LLM 如何理解詞序](https://www.analyticsvidhya.com/blog/2026/11/positional-embeddings-explained-llm-word-order/)
*Analytics Vidhya · 2026-11-22 · 相關度 5.06 · 必讀*

- **內容**：用「狗追狐狸 vs 狐狸追狗」的例子說明 transformer 本身沒有順序概念，必須靠 positional embeddings 告訴模型每個 token 的位置。
- **對你的意義**：DE 很熟資料順序與分區，但對 LLM 內部如何表示順序通常是黑盒；理解位置編碼才能解釋 long context 衰減、chunk 切太長失準等 RAG 實務問題。
- **今天可以做**：讀完後用自己的話寫 200 字筆記，說明 absolute 與 relative 位置編碼差異，並連結到你未來 RAG chunk size 的選擇理由。
- **原文標題**：Positional Embeddings Explained: How LLMs Understand Word Order
- `#LLM基礎` `#transformer` `#embedding` `#RAG`

### [Perplexity 與智慧：模型評估的共同語言](https://openai.com/index/perplexity-and-intelligence)
*OpenAI News · 2026-11-22 · 相關度 4.4 · 必讀*

- **內容**：OpenAI 說明 perplexity 如何衡量模型進展，以及為何它可能成為開發者評估新興能力的共同基準。
- **對你的意義**：評估能力是 DE 轉 AI Engineer 最關鍵的落差；你需要分得清 perplexity 這類模型層指標，與 RAG/Agent 系統層的任務指標該怎麼搭配使用。
- **今天可以做**：讀完後畫一張兩欄表：左欄模型層指標（perplexity 等）、右欄應用層指標（正確率、faithfulness、latency、成本），各寫出適用場景。
- **原文標題**：Perplexity and Intelligence
- `#模型評估` `#LLMOps` `#指標`

### [AI 如何改變資料科學的四類分析](https://towardsdatascience.com/how-ai-changes-the-four-types-of-analytics-for-data-scientists/)
*Towards Data Science · 2026-11-22 · 相關度 3.55 · 必讀*

- **內容**：主張把 AI agent 當成初階隊友，人類往上移動到問題定義、模型評估與業務協作這些更高抽象層。
- **對你的意義**：直接回答你的轉職定位問題：AI Engineer 的價值不在寫更多程式，而在定義問題、設計評估與承擔上線後果。
- **今天可以做**：用這個框架重寫一份自己的履歷段落，把過去 pipeline 經驗改寫成「問題定義＋評估指標＋業務成果」三段式。
- **原文標題**：How AI Changes the Four Types of Analytics for Data Scientists
- `#職涯定位` `#評估` `#agent協作`

## 👀 值得快速瀏覽（3）

*掃過標題與重點即可*

### [Muru：AI 協作開發的 Rust Python 伺服器](https://simonwillison.net/2026/Nov/21/muru/)
*Simon Willison's Weblog · 2026-11-21 · 相關度 5.04 · 快速瀏覽*

- **內容**：mod_wsgi 作者推出新的 Rust 實作 ASGI/WSGI 伺服器 Muru，並以極詳細的開發日誌公開整個 AI 輔助開發過程。
- **對你的意義**：對轉職者而言，價值不在 Muru 本身，而在觀察資深工程師如何把 AI 當成共同開發者來推進一個系統級專案的工作流。
- **今天可以做**：花 10 分鐘掃其中一篇開發日誌，記下他交派給 AI 的任務類型與他自己保留的決策，整理成自己的 AI 協作守則。
- **原文標題**：Muru
- `#AI輔助開發` `#工程實務` `#Python服務`

### [我們本來不想寫書，但想寫那本書](https://www.ssp.sh/blog/cynthia-dunlop-writing-books/)
*Simon Späti – Data Engineering Design · 2026-11-22 · 相關度 4.71 · 快速瀏覽*

- **內容**：Cynthia Dunlop 分享她從文學背景跨入技術寫作、共同著作六本書的流程，包括筆記取材、隔夜再編修，以及她如何（或不）使用 AI 協助寫作。
- **對你的意義**：轉職 AI Engineer 很吃「把複雜系統講清楚」的能力，面試與技術文件都靠它；她的筆記到成文流程可直接複用在你的學習輸出上。
- **今天可以做**：挑一個她的方法（例如先累積筆記再成文、草稿隔夜再改）套用到今天的學習筆記，產出一篇短文並隔天再修。
- **原文標題**：We didn't really want to write a book. But we wanted to write that book—Cynthia Dunlop (Show Your Workflow #2)
- `#職涯` `#技術寫作` `#學習方法`

### [AWS Quick 更新：更強的 flows 與多 agent 協作](https://aws.amazon.com/blogs/machine-learning/new-in-aws-quick-more-capable-flows-an-updated-web-experience-and-agents-that-work-together/)
*AWS Machine Learning Blog · 2026-11-21 · 相關度 3.38 · 快速瀏覽*

- **內容**：AWS Quick 推出在對話中建立業務流程 flows、更新的 web 介面、多 agent 同時回答，以及 Meta ads、Amplitude 等新資料來源。
- **對你的意義**：多 agent 協作與 flow 編排正是 Airflow DAG 思維的下一代版本；你能用既有編排經驗理解它的可靠性、重試與狀態管理挑戰。
- **今天可以做**：列出你熟悉的 Airflow 概念（DAG、retry、idempotency、backfill）各自在多 agent flow 中對應什麼，寫成一頁對照表。
- **原文標題**：New in AWS Quick: More capable flows, an updated web experience, and agents that work together
- `#agent編排` `#工作流` `#AWS`

## 🗂️ 存起來參考（3）

*之後需要時再回頭看*

### [RANSAC 解析：影像特徵匹配的共識擬合](https://towardsdatascience.com/ransac-explained-consensus-fitting-for-image-feature-matching/)
*Towards Data Science · 2026-11-22 · 相關度 5.0 · 存參考*

- **內容**：說明如何用隨機抽樣 4 組匹配點、誤差門檻與 inlier 計數，把雜訊很多的 SIFT 匹配轉成可靠的 homography 矩陣。
- **對你的意義**：與 LLM 路線關聯較低，但 RANSAC 的「從雜訊中找共識」思維，和 LLM 多次取樣再投票（self-consistency）有相通之處，可當作概念類比。
- **今天可以做**：若時間有餘，只讀 inlier/outlier 的定義段落，並在筆記寫下它與 LLM self-consistency 投票的一句類比。
- **原文標題**：RANSAC, Explained: Consensus Fitting for Image Feature Matching
- `#CV` `#演算法` `#穩健估計`

### [AWS Quick 新增 Meta ads 連接器](https://aws.amazon.com/blogs/machine-learning/meta-ads-is-now-available-in-aws-quick/)
*AWS Machine Learning Blog · 2026-11-22 · 相關度 4.2 · 存參考*

- **內容**：AWS Quick 推出 Meta ads AI connector，使用者能用自然語言建立、管理與分析廣告活動，並把 Meta 廣告資料與第一、三方資料結合成儀表板與自動化工作流。
- **對你的意義**：這正是 DE 的強項戰場：資料源整合＋語意層治理，只是介面換成自然語言與 agent，可當作你把既有整合經驗轉譯成 AI 產品語言的案例。
- **今天可以做**：對照你做過的一條外部 API 資料接入流程，寫下若改成自然語言 agent 操作，哪些 schema 與權限控管必須先定義好。
- **原文標題**：Meta ads is now available in AWS Quick
- `#AWS` `#資料整合` `#agent工作流`

### [Google Duplex 進化：在 Gemini 中代你致電商家](https://research.google/blog/how-google-duplex-evolved-to-also-call-businesses-for-you-in-gemini/)
*Google Research Blog · 2026-11-20 · 相關度 3.11 · 存參考*

- **內容**：介紹 Duplex 技術如何演進並整合進 Gemini，代替使用者打電話給商家。摘要資訊有限，僅標示為生成式 AI 主題。
- **對你的意義**：這是少見的「agent 真的對外執行動作」產品案例，可觀察真實世界 action agent 在可靠性、確認機制與風險控管上的設計取捨。
- **今天可以做**：花 5 分鐘瀏覽原文，記下它在「失敗時如何回退給人類」的機制，作為你未來設計 agent 護欄的參考。
- **原文標題**：How Google Duplex evolved to also call businesses for you in Gemini
- `#agent` `#語音AI` `#Google`

## 🎯 今天的 30 分鐘學習計畫

1. 先花 10 分鐘讀 OpenAI 的 Perplexity and Intelligence，把 perplexity 與你會用到的 LLM 應用層指標（faithfulness、answer relevancy）寫成一張對照筆記，釐清「模型層指標」與「系統層指標」的分工。
2. 用 10 分鐘讀 positional embeddings 說明，並在筆記寫下：為什麼 RAG chunking 的長度與順序會受 context window／位置編碼影響，列出 2 個對自己未來 RAG 設計的具體啟示。
3. 最後 10 分鐘掃過 AWS Quick 的 agents 協作更新與 TDS 的四類分析文章，對照自己現有的一條 Airflow pipeline，寫下「哪一段可以改成 agent + connector 執行、哪一段必須保留確定性排程」的判斷。

---

掃描 15 篇，收錄 9 篇。來源分布：Towards Data Science × 2、AWS Machine Learning Blog × 2、Analytics Vidhya × 1、Simon Willison's Weblog × 1、Simon Späti – Data Engineering Design × 1、OpenAI News × 1、Google Research Blog × 1

> ⚠️ [Uber Engineering Blog](https://www.uber.com/en-US/blog/engineering/)：官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。

*由 ai-data-digest 於 2026-11-23 04:46 自動產生 · 摘要引擎：Claude（claude-opus-5）*