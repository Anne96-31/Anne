# 從零做出「AI 學習筆記」的 RAG + MCP：給 Data Engineer 的白話教學

> 目標：把每天收到的 AI & Data 摘要（`digests/`）變成**可以問問題、會附來源**的知識庫，
> 再透過 **MCP** 讓 Claude Code、Claude Desktop 這類 AI 工具直接查你的筆記。
>
> 參考解答都在 [`airag/`](../airag/)。建議**每一步先自己寫**，卡住或寫完再對照。

---

## 0. 先用一個比喻看懂全貌

**RAG 就像「開書考」。**

| 開書考 | RAG | 這個專案的檔案 |
|---|---|---|
| 把課本整理成一張張重點卡 | **切塊（Chunking）** | `corpus.py` |
| 考試時翻目錄找到相關的頁 | **檢索（Retrieval）** | `index.py` |
| 只根據翻到的那幾頁作答，並寫出「見第幾頁」 | **生成（Generation）＋引用** | `answer.py` |
| 拿考古題測試自己翻書夠不夠快、夠不夠準 | **評估（Evaluation）** | `evaluate.py` |

**MCP 就像「USB-C 插座」。**
你把功能（例如「搜尋筆記」）做成符合 MCP 規格的插頭，任何支援 MCP 的 AI 工具插上去就能用，
不用替 Claude Code、Claude Desktop、Cursor 各寫一套。

```
                         ┌──────────────── 你的 RAG ────────────────┐
digests/*.md ──切塊──▶ chunks ──建索引──▶ BM25 index ──檢索──▶ 前 5 篇 ──▶ Claude 生成（附 [S1] 引用）
                                              ▲
                                              │ search_notes(query)
                         Claude Code / Desktop ┘  ← 透過 MCP 呼叫
```

**RAG 和 MCP 不是同一層的東西：**
- RAG 是一種**做法**（先查資料再回答）。
- MCP 是一個**介面標準**（讓 AI 工具呼叫你的程式）。
- 這個專案把 RAG 的「檢索」包成 MCP 工具，AI 就能**自己決定什麼時候去查**，這叫 *agentic RAG*。

### 環境準備

```bash
pip install -r requirements-rag.txt pytest
```

```bash
python -m airag stats
```

`stats` 會顯示語料規模，例如「chunk：437（文章 406、每日重點 31）」。

---

## 第 1 步：切塊——把 Markdown 變成「重點卡」（你的 DE 主場）

### 觀念
LLM 一次讀不了全部筆記，也不該讀全部，因為無關的內容會干擾回答。所以要先把資料切成小塊（chunk），每塊附上 metadata（日期、來源、標籤）。

**最常見的錯誤是固定每 500 字切一刀。** 這樣常把一則新聞切成兩半，前半段有標題、後半段沒有，檢索就會失準。
我們的摘要本身就是一張張「文章卡片」（`### [標題](網址)` 開頭），所以**一張卡片 = 一個 chunk**，
另外把每天的「今日重點」也當成一個 chunk，用來回答「那段時間的趨勢是什麼」這類問題。

> 💡 這就是 DE 的優勢：**切塊本質上是資料建模**。要依資料的自然結構切，並保留可以拿來過濾的欄位。

### 你要寫的東西
```python
@dataclass(frozen=True)
class Chunk:
    chunk_id: str; date: str; kind: str       # kind = "article" 或 "briefing"
    title: str; url: str; source: str; priority: str
    summary: str; why: str; action: str; tags: tuple[str, ...]

def parse_digest(markdown: str, date: str) -> list[Chunk]: ...
def load_corpus(directory: Path) -> list[Chunk]: ...   # 讀所有 YYYY-MM-DD.md
```

### 提示
- 用正規表示式抓 `### [標題](網址)`、`*來源 · 日期 · 相關度 x · 必讀*`、`- **內容**：...`。
- 逐行掃描：遇到新的 `###` 就把上一張卡存起來（這叫 flush）。
- `latest.md` 和其他檔案內容重複，不要讀進來。
- 同一個網址可能在兩天都出現，只保留最新的那張（去重 = DE 日常）。

### 自我檢查
```bash
python -m pytest -q tests/test_airag.py -k parse
```
預期：chunk 數量等於所有 `### [` 標題的數量（扣掉重複的網址）。

---

## 第 2 步：檢索——用 BM25 在 400 張卡片裡找答案

### 觀念：BM25 只看三件事
想像你在找「**MCP 案例**」：

1. **詞頻（tf）**：卡片裡「MCP」出現越多次，越可能相關。但出現 10 次不會比出現 5 次重要一倍，效果會**遞減**。
2. **稀有度（idf）**：「的」每張卡片都有，沒有參考價值；「MCP」只有少數卡片有，命中它就很有意義。**越稀有的詞，權重越高**。
3. **長度正規化**：長文章本來就容易什麼詞都有，所以要扣一點分，避免長文佔便宜。

把每個查詢詞的分數加總，就是這張卡片的分數。公式看起來嚇人，其實就是上面三件事。實作只有約 30 行，見 `index.py` 的 `search()`。

### 為什麼不用 embedding（向量）？
- 語料只有約 400 篇，又充滿專有名詞（RAG、vLLM、Databricks），**詞彙比對本來就很強**。
- BM25 不需要模型、不需要 GPU，而且**看得到命中了哪些詞**，除錯很容易。
- 我們的筆記裡就有一篇文章（2026-11-14〈選 Agent 工具時，關鍵字搜尋打平 8B embedding〉）的結論是：BM25 和 8B 的 embedding 模型打平，速度還快 40 倍。
- **先做簡單、能量化的基準，再決定要不要加 embedding**，這是面試官想聽到的工程判斷。

### 中文怎麼辦？用「字元 bigram」
中文沒有空格，「檢索評估」要怎麼切成詞？最簡單的方法是兩個字兩個字切：
`檢索評估` → `檢索`、`索評`、`評估`。
「索評」雖然沒有意義，但它幾乎不會出現在別的地方，不會造成干擾。這樣就不需要另外裝斷詞套件。

### 中英對不上怎麼辦？用同義詞擴充
問「檢索增強」時，文章裡寫的卻是「RAG」。做法是準備一張小型同義詞表：
查詢裡出現某個詞，就把同一組的其他詞以較低權重（0.5）加進查詢。

### 你要寫的東西
```python
def tokenize(text: str) -> list[str]: ...          # 英文小寫 + 中文 bigram
class BM25Index:
    def __init__(self, chunks): ...                  # 預先算好每張卡片的詞頻與每個詞的 idf
    def search(self, query, k=5, date_from=None, priority=None, tag=None) -> list[Hit]: ...
```

### 自我檢查
```bash
python -m airag search "MCP 多租戶"
```
預期：第一名是 MoEngage 那篇，下面會列出「命中詞」。

```bash
python -m airag search "RAG" --from 2026-11-10 --priority must_read
```
預期：只列出 11/10 之後、標記為必讀的文章（metadata 過濾）。

---

## 第 3 步：評估——用「考古題」證明你的檢索真的有用（面試最加分）

### 觀念
「我覺得變好了」不算數，要有數字。做法是準備一份**黃金測試集**：每題寫好「問題 → 正確文章」。

| 指標 | 白話意思 |
|---|---|
| **hit@5** | 正確答案有沒有出現在前 5 名？44 題中有幾題做到 |
| **MRR** | 正確答案排第 1 名得 1 分、第 2 名得 0.5 分、第 3 名得 0.33 分，沒找到得 0 分，最後取平均。比 hit@5 更在意「排得夠不夠前面」 |

### 我們實際踩到的坑（很好的面試故事）
1. **第一版題目太簡單，所有設定都拿到一樣的分數。**
   原因是我看著文章標題出題，題目用詞跟標題幾乎一樣，怎麼搜都找得到。
   👉 教訓：**出題時不能偷看答案的用詞**。我們補了 20 題「換句話說、中英交叉」的困難題，
   例如英文問 *"agents owned by different organizations talking to each other"*，答案是中文標題的 A2A 文章。

2. **直覺覺得有用的設計，數據說不一定。**
   消融實驗（一次關掉一個設計，看分數掉多少）的結果，困難題 20 題：

   | 設定 | hit@1 | hit@5 | MRR |
   |---|---|---|---|
   | 預設（中文 bigram + 中英同義詞） | 0.75 | **0.95** | 0.805 |
   | 拿掉中英同義詞擴充 | 0.75 | 0.90 | 0.808 |
   | 加上標題/tag 加權 | 0.70 | 0.90 | 0.764 |
   | 中文改用單字（不用 bigram） | 0.65 | 0.85 | 0.718 |

   - **bigram 明顯有用**：改成單字切詞後，MRR 從 0.805 掉到 0.718。
   - **「標題加權」反而變差**：原本以為標題很重要，但使用者的問法常常跟標題不一樣，所以預設改成關閉。
   - **同義詞擴充讓 hit@5 從 0.90 提升到 0.95**，MRR 幾乎沒變，代表它的作用是「把漏掉的找回來」。

3. **測試集小時不要過度調參。** 20 題裡面，一題就差 0.05。差距這麼小時，不要為了刷分一直改參數。

4. **評估語料要凍結。** `digests/` 只保留 30 天，所以把 8 天的摘要複製到 `airag/eval/corpus/`，
   之後改程式時，分數的差異才只來自程式本身，不會因為資料變動而飄。

### 自我檢查
```bash
python -m airag eval --ablation
```

```bash
python -m airag eval --ablation --difficulty hard
```

`tests/test_airag.py` 裡有**回歸門檻**：hit@5 低於 0.85 時測試就會失敗。改壞檢索時，CI 會擋下來。

---

## 第 4 步：生成——讓 Claude 根據筆記回答，而且不能亂講

### 觀念
把前 5 篇編號成 `[S1]`～`[S5]` 放進 prompt，要求 Claude **只能根據這些來源回答，每個論點都要標上來源編號**。

**三道防線，避免幻覺：**
1. **檢索不到就不問 LLM**：直接回「找不到相關筆記」。這樣既省錢，也不給它瞎編的機會。
2. **Structured output**：用 JSON schema 固定輸出格式 `{answer, insufficient_context, follow_up}`，
   還多了一個「資料不足」的欄位，讓它可以合法地說「我不知道」。
3. **程式檢查引用**：只給了 5 篇卻引用 `[S7]`，就把它刪掉並記錄下來。

另外還有**退路**：沒有 API key、額度用完或被拒答時，改成列出最相關的幾篇筆記（extractive），功能不會整個掛掉。

### 自我檢查
```bash
python -m airag ask "最近有哪些 MCP 的實際案例？" --no-llm
```

```bash
ANTHROPIC_API_KEY=sk-ant-xxx python -m airag ask "最近有哪些 MCP 的實際案例？"
```

第一條不需要 API key；第二條要把 `sk-ant-xxx` 換成你自己的 key。
沒有 API key 也能跑測試，因為 `tests/test_airag.py` 用假的 client 驗證了「引用檢查」和「拒答退路」的邏輯。

---

## 第 5 步：MCP server——把檢索插上「USB-C」

### 觀念
MCP 有兩種主要的東西：
- **tool（工具）**：AI 會**主動呼叫**的動作。我們提供 `search_notes`、`ask_notes`、`list_digests`、`get_digest`。
- **resource（資源）**：可以被**讀取**的資料，像檔案一樣。我們提供 `notes://latest`、`notes://2026-11-17`。

AI 怎麼知道什麼時候該用哪個工具？**靠你寫的函式說明（docstring）和參數型別**。
MCP SDK 會自動把它們轉成工具說明給 AI 看，所以**工具說明要寫得像給新同事的交接文件**。

### 最小可用版本（約 15 行，先寫出這個就成功一半）
```python
from mcp.server.mcpserver import MCPServer   # ⚠️ mcp 2.x 的寫法；舊教學的 FastMCP 已經改名
from airag.index import load_index

server = MCPServer("my-ai-notes")

@server.tool()
def search_notes(query: str, k: int = 5) -> list[dict]:
    """搜尋我的 AI 學習筆記，回傳最相關的文章與連結。query 中英文皆可。"""
    hits = load_index("digests").search(query, k=k)
    return [h.to_dict() for h in hits]

if __name__ == "__main__":
    server.run("stdio")
```

### 上線前要補的「工程細節」（這些才是面試會問的）
- **唯讀**：標上 `read_only_hint=True`，讓客戶端知道這個工具很安全。
- **輸入驗證**：`get_digest("../../etc/passwd")` 必須被擋下來。我們只接受 `YYYY-MM-DD` 格式的日期，檔名只由日期組成。
- **上限**：`k` 最大 20，避免一次回傳太多內容，把 AI 的 context 塞爆。
- **型別化輸出**：用 pydantic model（`SearchResult`）定義回傳格式，客戶端會拿到 output schema。
- **自動重建索引**：用檔案指紋（檔名、修改時間、大小）當快取的 key，每天有新摘要進來時會自動重建。

### 接到 Claude Code 試試看
在 Anne 資料夾裡執行，把 `/你的/路徑/Anne` 換成實際路徑（Windows 寫成 `C:\Users\...\Anne`）：

```bash
claude mcp add anne-notes -e PYTHONPATH=/你的/路徑/Anne -- python -m airag.mcp_server
```

接著在 Claude Code 裡問：「我最近讀過哪些跟 GraphRAG 有關的文章？」
如果它呼叫了 `search_notes`，回答附上你的筆記連結，就代表成功了。

### 自我檢查
```bash
python -m pytest -q tests/test_airag.py -k mcp
```
這些測試會用 MCP 官方的 `Client` 在同一個程式裡連上 server，驗證工具清單、搜尋結果，以及惡意輸入會被擋下。

---

## 第 6 步（進階選做）：你可以接著挑戰的題目

1. **加上 embedding，做 hybrid 檢索**：BM25 和向量檢索各排一次，再用 RRF（Reciprocal Rank Fusion）合併。
   **用第 3 步的評估集證明它有沒有比較好。** 沒變好也是一個有價值的結論。
2. **不要再讓筆記消失**：現在 `digests/` 只留 30 天。可以把舊的 chunk 存進 SQLite 或 DuckDB，讓知識庫持續累積（DE 主場）。
3. **評估生成品質**：現在只評估了檢索。可以用 LLM-as-a-judge 評估「回答是否忠於來源（faithfulness）」。

---

## 🎤 面試 30 秒版本

> 「我每天用自動化流程收 AI 產業摘要，一個月累積 400 多則，卻沒辦法查。所以我做了一個 RAG：
> 依文章卡片切塊並保留 metadata，用中英混合的 BM25 檢索，中文用 bigram，再加上中英同義詞擴充；
> 生成時用 structured output 和程式檢查引用，避免幻覺。
> 我建了 44 題的評估集，發現第一版題目太簡單、分數沒有鑑別度，所以補了換句話說和中英交叉的困難題；
> 消融實驗也推翻了我原本以為有用的標題加權。最後困難題的 hit@5 是 0.95。
> 檢索功能包成 MCP server，Claude Code 可以直接查我的筆記，CI 也會用評估門檻擋下品質退步。」

這段話裡的每一個細節都是你真的做過的，被追問也答得出來。
