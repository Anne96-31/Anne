# 第 1 課：Spark 的心智模型

> 🎯 學習目標：在腦中建立「Spark 怎麼運作」的畫面。之後所有的調校和除錯，都從這個畫面出發。

## 1. Spark 解決什麼問題？

假設有 1 TB 的訂單資料，要算每個國家的營收：

- **一台電腦**：記憶體放不下，硬跑也要好幾個小時
- **Spark**：把資料切成 1,000 小塊，分給 50 台機器同時算，幾分鐘完成

### 比喻：餐廳廚房

| Spark | 廚房 | 做什麼 |
|---|---|---|
| Driver | 主廚 | 看菜單（你的程式）、規劃步驟、分派工作，自己不切菜 |
| Executor | 廚師 | 實際處理食材（資料） |
| Partition | 一籃食材 | 一位廚師一次處理一籃 |
| Task | 一張工作單 | 「處理這一籃」 |

```text
          ┌──────── Driver（主廚）────────┐
          │  讀程式 → 規劃 → 分派工作      │
          └─────┬──────────┬──────────┬───┘
                ▼          ▼          ▼
           Executor 1  Executor 2  Executor 3
           [P1][P2]    [P3][P4]    [P5][P6]
```

- **Partition 數 ≈ 平行度**：只有 2 個 partition 的話，就算有 100 個 core 也只會用到 2 個。

> ⚠️ 地雷：`collect()` 會把所有資料搬回 Driver，就像叫 50 位廚師把食材全堆到主廚一個人的砧板上，Driver 會記憶體不足（OOM）。改用 `show()`、`take(n)`、`limit(n)`，或直接寫出檔案。

## 2. Spark 很「懶」（Lazy Evaluation）

| 類型 | 例子 | 會馬上執行嗎？ |
|---|---|---|
| Transformation（轉換） | select、filter、withColumn、join、groupBy | ❌ 只寫進計畫 |
| Action（動作） | show、count、collect、write | ✅ 這時才開工 |

```python
df  = spark.read.parquet("/data/orders")   # 0.1 秒：只記下「要讀這裡」
tw  = df.filter(df.country == "TW")        # 0.1 秒：只記下「要篩選」
res = tw.select("order_id", "amount")      # 0.1 秒：只記下「要選欄位」
res.count()                                # 3 分鐘：這時才真正讀資料、計算
```

**為什麼要懶？** 主廚把整張菜單看完再分工，才能想出最省事的做法。Spark 的優化器 **Catalyst** 看完整條流程後，會自動：

- **Predicate pushdown**：讀檔時就先篩掉不是 TW 的資料
- **Column pruning**：只讀需要的欄位，其他欄位碰都不碰

> 💡 實務提醒：notebook 裡一行轉換「瞬間跑完」不代表沒問題，錯誤常常要到 action 才會出現。除錯時要往前看整條流程。

## 3. Narrow vs Wide：決定速度的關鍵

### Narrow transformation（快）

每個 partition 自己處理，不需要跟別人交換資料。例子：`filter`、`select`、`withColumn`。

```text
P1 → filter → P1'
P2 → filter → P2'      各做各的，不用溝通
```

### Wide transformation（慢）

需要把相同 key 的資料集中到同一處，這個搬運過程叫 **Shuffle**。例子：`groupBy`、`join`、`orderBy`、`distinct`。

```text
P1 [TW, JP, US] ─┐        ┌─▶ [TW, TW, TW]
P2 [JP, TW, US] ─┼─ 搬 ─┼─▶ [JP, JP]
P3 [US, TW, JP] ─┘        └─▶ [US, US, US]
```

Shuffle 很貴的原因：

1. 資料要先寫到磁碟
2. 透過網路傳到別台機器
3. 接收端再讀進來

### Job、Stage、Task 的關係

```text
一個 Action  →  一個 Job
                 ├── Stage 1：read → filter → select   （narrow 串成一段）
                 │       ══ shuffle ══                  ← 切出新的 stage
                 └── Stage 2：groupBy 聚合 → 輸出
                       每個 Stage 有很多 Task（一個 partition 一個 task）
```

- **規則：每遇到一次 shuffle，就切出一個新的 Stage。**

> 💡 本課重點：Spark 調校的核心 = 減少 shuffle + 讓 partition 大小平均。

## 4. 完整例子：把三件事串起來

```python
(spark.read.parquet("/data/orders")      # 轉換
   .filter("country = 'TW'")             # 轉換，narrow
   .groupBy("city")                      # 轉換，wide → 會 shuffle
   .sum("amount")                        # 轉換
   .write.saveAsTable("tw_city_rev"))    # 動作 → 觸發 Job
```

1. 前面幾行只建立計畫，什麼都沒執行
2. 執行到 `write` 才建立一個 Job
3. Catalyst 優化：只讀需要的欄位、讀檔時就篩選 TW
4. **Stage 1**：每個 Executor 讀自己的 partition、篩選，並先在本地做部分加總（partial aggregation，讓 shuffle 少搬很多資料）
5. **Shuffle**：同一城市的部分結果送到同一處
6. **Stage 2**：合併成最終加總，寫成資料表

## 5. 重點整理

- Driver 規劃、Executor 執行，Partition 決定平行度
- Transformation 只記計畫，Action 才執行；懶惰讓 Catalyst 能優化
- Narrow 快、Wide 慢；每次 shuffle 切一個新 Stage
- 不要對大資料 `collect()`

## 6. 隨堂測驗

1. 為什麼 `df.filter(...)` 一下子就跑完，`df.count()` 卻很久？
2. `df.filter(col("country") == "TW").groupBy("city").count().orderBy("count").show()` 大約會切成幾個 Stage？為什麼？
3. 為什麼對 1 億筆的 DataFrame 呼叫 `collect()` 很危險？應該改用什麼？
4. （思考題）要 join 一張 10 億筆的訂單表和一張只有 200 筆的國家代碼表，Spark 可以怎麼做，才不用讓 10 億筆訂單去 shuffle？

<details>
<summary>參考答案（先自己想過再打開）</summary>

1. `filter` 是 transformation，只記錄計畫；`count` 是 action，才真正讀資料計算。
2. 大約 3 個：filter 那段 →（shuffle）→ groupBy 聚合 →（shuffle）→ orderBy。實際數量會受 AQE 等優化影響，可以在 Spark UI 驗證。
3. 所有資料會被拉回 Driver 的記憶體，容易 OOM。改用 `show()`、`take(n)`、`limit(n)`，或直接寫成檔案。
4. **Broadcast join**：把 200 筆的小表複製一份給每個 Executor，每台機器拿自己手上的訂單直接對照，大表完全不用搬。寫法是 `orders.join(broadcast(countries), "country_code")`，第 3 課會詳細介紹。

</details>
