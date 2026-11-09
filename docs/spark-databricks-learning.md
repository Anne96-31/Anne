# ⚡ Spark & Databricks 學習指南

> 給 Data Engineer 往 AI Engineer 發展的學習路線。目標：**8 週**內能獨立用 Databricks 建一條 Medallion 資料管線，並考取 Databricks Data Engineer Associate 認證。

---

## 目錄

1. [學習路線（8 週）](#1-學習路線8-週)
2. [學習資源](#2-學習資源)
3. [第 1 課：Spark 的心智模型](#第-1-課spark-的心智模型)
4. [第 2 課：DataFrame 實戰](#第-2-課dataframe-實戰)
5. [第 3 課：效能調校入門](#第-3-課效能調校入門)
6. [第 4 課：Databricks 平台與 Delta Lake](#第-4-課databricks-平台與-delta-lake)
7. [期末專案](#期末專案)
8. [面試常考題](#面試常考題)

---

## 1. 學習路線（8 週）

| 週 | 主題 | 產出 |
|---|---|---|
| 1 | Spark 架構：Driver / Executor、Lazy evaluation、Transformation vs Action | 能畫出一個 job 怎麼被拆成 stage 和 task |
| 2 | DataFrame API + Spark SQL：select / filter / groupBy / join / window | 完成第 2 課練習 |
| 3 | 效能：Partition、Shuffle、Broadcast join、AQE、快取、Spark UI | 能從 Spark UI 找出慢的 stage |
| 4 | Databricks 平台：Workspace、Notebook、Compute、Serverless、Unity Catalog | 在 Free Edition 跑起第一個 notebook |
| 5 | Delta Lake：ACID、Time Travel、MERGE、OPTIMIZE、Liquid Clustering | 寫出一個 upsert（MERGE）流程 |
| 6 | 增量處理：Structured Streaming、Auto Loader、Lakeflow Declarative Pipelines（舊名 DLT） | Bronze → Silver → Gold 管線 |
| 7 | 排程與治理：Lakeflow Jobs、Unity Catalog 權限、Databricks SQL Dashboard | 管線每天自動跑 |
| 8 | AI on Databricks：MLflow、Vector Search、Model Serving、Agent 開發 + 認證衝刺 | 期末專案 + 報名考試 |

**每天建議：** 30 分鐘讀概念 + 30 分鐘寫程式。週末做一次小專案整合。

---

## 2. 學習資源

### 🆓 免費練習環境

| 資源 | 說明 |
|---|---|
| [Databricks Free Edition](https://www.databricks.com/learn/free-edition) | 官方免費版（取代舊的 Community Edition），有 Serverless、Unity Catalog、SQL，**首選** |
| 本機 PySpark | `pip install pyspark`，需要 Java 17+。適合學 Spark 核心，不含 Databricks 功能 |
| Google Colab | `!pip install pyspark` 即可，免裝 Java |

### 📚 書籍

| 書 | 適合 | 備註 |
|---|---|---|
| *Learning Spark, 2nd Edition*（O'Reilly） | 入門首選 | Databricks 官網可免費下載電子版 |
| *Spark: The Definitive Guide*（O'Reilly） | 想深入原理 | 版本較舊，但架構概念仍適用 |
| *Delta Lake: The Definitive Guide*（O'Reilly） | 第 5 週後 | Databricks 也有免費版 |

### 🎓 課程

| 課程 | 說明 |
|---|---|
| [Databricks Academy](https://www.databricks.com/learn/training/home) | 官方免費自學課程，**Data Engineering with Databricks** 是認證必修路線 |
| Databricks 官方 YouTube | Data + AI Summit 演講，看最新功能 |
| Udemy：Derar Alhussein 的 Databricks 認證系列 | 考試準備口碑好（付費，常特價） |

### 📖 官方文件（遇到問題先查這裡）

- Spark 文件：<https://spark.apache.org/docs/latest/>
- PySpark API：<https://spark.apache.org/docs/latest/api/python/>
- Databricks 文件：<https://docs.databricks.com/>
- Delta Lake 文件：<https://docs.delta.io/>

### 🏅 認證路線

1. **Databricks Certified Data Engineer Associate** ← 先考這張
2. Databricks Certified Associate Developer for Apache Spark（偏 Spark API）
3. Databricks Certified Data Engineer Professional
4. 轉 AI 方向：Databricks Certified Generative AI Engineer Associate

> 考試大綱會更新，報名前請到 Databricks 認證頁確認最新版本。

---

## 第 1 課：Spark 的心智模型

### 1.1 Spark 解決什麼問題？

資料大到一台電腦放不下或算太慢時，Spark 把資料**切成很多塊（partition）**，分給很多台機器**同時算**，最後把結果合起來。

```
           ┌──────────── Driver（大腦）────────────┐
           │  你的程式 → 規劃執行計畫 → 分派任務  │
           └───────┬───────────┬───────────┬───────┘
                   ▼           ▼           ▼
             Executor 1   Executor 2   Executor 3   （工人）
             [P1][P2]     [P3][P4]     [P5][P6]     ← 每個 partition 一個 task
```

- **Driver**：執行你的程式、建立執行計畫、分派工作。`collect()` 會把資料拉回 Driver，資料太大會讓它爆掉。
- **Executor**：真正處理資料的工人，每個 core 一次處理一個 task。
- **Partition**：資料的一小塊。**partition 數 ≈ 平行度**。

### 1.2 Lazy Evaluation：Spark 很「懶」

Spark 的操作分兩種：

| 類型 | 例子 | 會馬上執行嗎？ |
|---|---|---|
| **Transformation**（轉換） | `select`, `filter`, `withColumn`, `join`, `groupBy` | ❌ 只記下來 |
| **Action**（動作） | `show`, `count`, `collect`, `write`, `display` | ✅ 觸發執行 |

```python
df = spark.read.parquet("/data/orders")    # 還沒讀
big = df.filter(df.amount > 1000)           # 還沒算
result = big.select("order_id", "amount")   # 還沒算
result.count()                              # ← 這時才真正執行全部
```

**為什麼要懶？** 因為 Spark 看完整個流程才動手，優化器（Catalyst）就能幫你重排：例如先 filter 再讀需要的欄位（predicate pushdown / column pruning），少讀很多資料。

### 1.3 Narrow vs Wide：效能的關鍵

- **Narrow transformation**（`filter`, `select`, `withColumn`）：每個 partition 自己算，不用跟別人交換資料，**快**。
- **Wide transformation**（`groupBy`, `join`, `orderBy`, `distinct`）：需要把相同 key 的資料搬到同一台機器，叫 **Shuffle**，要走網路和寫磁碟，**慢**。

每遇到一次 shuffle，Spark 就切出一個新的 **Stage**。

```
Job（一個 action 觸發一個 job）
 ├── Stage 1：read → filter → select        （narrow，一路串起來）
 │      ── shuffle ──
 └── Stage 2：groupBy 聚合 → write
        每個 stage 由很多 task 組成（一個 partition 一個 task）
```

> 💡 **記住一句話：Spark 調校的核心就是減少 shuffle、讓 partition 大小平均。**

### ✏️ 第 1 課練習

1. 用自己的話解釋：為什麼 `df.filter(...)` 執行起來幾乎不花時間，但 `df.count()` 很久？
2. 下面程式會產生幾個 stage？
   ```python
   df.filter(col("country") == "TW").groupBy("city").count().orderBy("count").show()
   ```
3. 為什麼對一個 1 億筆的 DataFrame 呼叫 `collect()` 是危險的？

<details>
<summary>參考答案</summary>

1. `filter` 是 transformation，只是記錄計畫；`count` 是 action，才真正讀資料計算。
2. 大約 3 個：filter 那段 → (shuffle) → groupBy 聚合 → (shuffle) → orderBy。實際數量會受 AQE 等優化影響，可在 Spark UI 驗證。
3. `collect()` 把所有資料拉回 Driver 記憶體，資料太大會 OOM。改用 `show()`、`limit(n)`、`take(n)` 或直接寫出檔案。

</details>

---

## 第 2 課：DataFrame 實戰

以下程式在 **Databricks notebook** 或**本機 PySpark** 都能跑（本機要先建 `spark`，見最下方）。

### 2.1 建立資料

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

orders = spark.createDataFrame(
    [
        (1, "C01", "2026-11-01", "TW", 1200.0),
        (2, "C02", "2026-11-01", "JP",  300.0),
        (3, "C01", "2026-11-02", "TW",  800.0),
        (4, "C03", "2026-11-02", "US", 5000.0),
        (5, "C02", "2026-11-03", "JP", 1500.0),
        (6, "C01", "2026-11-03", "TW",  450.0),
    ],
    ["order_id", "customer_id", "order_date", "country", "amount"],
).withColumn("order_date", F.to_date("order_date"))

customers = spark.createDataFrame(
    [("C01", "Anne", "Gold"), ("C02", "Ken", "Silver"), ("C03", "Mia", "Gold")],
    ["customer_id", "name", "tier"],
)

orders.printSchema()
orders.show()
```

### 2.2 常用操作對照（PySpark ↔ SQL）

```python
# 選欄位 + 新增欄位
orders.select("order_id", "amount") \
      .withColumn("amount_twd", F.col("amount") * 32)

# 篩選
orders.filter((F.col("country") == "TW") & (F.col("amount") > 500))

# 分組聚合
orders.groupBy("country").agg(
    F.count("*").alias("n_orders"),
    F.sum("amount").alias("revenue"),
    F.round(F.avg("amount"), 1).alias("avg_amount"),
)

# Join
orders.join(customers, on="customer_id", how="left")

# 條件欄位（等於 SQL 的 CASE WHEN）
orders.withColumn(
    "size",
    F.when(F.col("amount") >= 1000, "big").otherwise("small"),
)
```

同樣的事用 SQL 寫：

```python
orders.createOrReplaceTempView("orders")
spark.sql("""
    SELECT country, COUNT(*) AS n_orders, SUM(amount) AS revenue
    FROM orders
    GROUP BY country
""").show()
```

> 💡 DataFrame API 和 Spark SQL **底層跑的是同一個優化器**，效能一樣，選順手的寫就好。

### 2.3 Window Function（面試必考）

每位客戶的「累計消費」與「第幾筆訂單」：

```python
w = Window.partitionBy("customer_id").orderBy("order_date")

orders.withColumn("order_seq", F.row_number().over(w)) \
      .withColumn("running_total", F.sum("amount").over(w)) \
      .withColumn("prev_amount", F.lag("amount").over(w)) \
      .orderBy("customer_id", "order_date") \
      .show()
```

### 2.4 看執行計畫

```python
orders.join(customers, "customer_id").groupBy("tier").sum("amount").explain("formatted")
```

在輸出裡找：
- `Exchange` → 這裡發生 **shuffle**
- `BroadcastHashJoin` → 小表被廣播，**不用 shuffle**（好事）
- `SortMergeJoin` → 兩邊都 shuffle 後排序（大表 join 大表時）

### ✏️ 第 2 課練習

1. 算出每個 `tier` 的總營收與訂單數。
2. 找出每位客戶**金額最大的那一筆訂單**（提示：`row_number` + `orderBy(desc)`，再 `filter(order_seq == 1)`）。
3. 算每天的營收，以及「與前一天相比的成長率」（提示：`lag`）。
4. 對第 1 題呼叫 `.explain()`，找出是哪種 join。

<details>
<summary>參考答案</summary>

```python
# 1
orders.join(customers, "customer_id") \
      .groupBy("tier") \
      .agg(F.sum("amount").alias("revenue"), F.count("*").alias("n_orders")) \
      .show()

# 2
w2 = Window.partitionBy("customer_id").orderBy(F.desc("amount"))
orders.withColumn("rk", F.row_number().over(w2)).filter("rk = 1").drop("rk").show()

# 3
daily = orders.groupBy("order_date").agg(F.sum("amount").alias("revenue"))
w3 = Window.orderBy("order_date")   # 沒有 partitionBy，資料會集中到一個 partition，只適合小資料
daily.withColumn("prev", F.lag("revenue").over(w3)) \
     .withColumn("growth_pct", F.round((F.col("revenue") / F.col("prev") - 1) * 100, 1)) \
     .show()

# 4：explain() 顯示的是「執行前」的計畫，可能是 SortMergeJoin，
#    外層包著 AdaptiveSparkPlan，代表 AQE 執行時可能自動改成 broadcast。
#    想確定用 broadcast，就自己指定：
orders.join(F.broadcast(customers), "customer_id").groupBy("tier").sum("amount").explain()
#    這時會看到 BroadcastHashJoin
```

</details>

---

## 第 3 課：效能調校入門

| 問題 | 症狀（Spark UI） | 解法 |
|---|---|---|
| **Data skew**（資料傾斜） | 某幾個 task 跑特別久 | 開 AQE skew join（Databricks 預設開）、對熱門 key 加 salt |
| **太多小檔案** | 讀取慢、task 數爆多 | Delta `OPTIMIZE`、寫出前 `coalesce` |
| **大表 join 小表很慢** | 出現 SortMergeJoin | `F.broadcast(small_df)` 強制廣播 |
| **Shuffle partition 不合適** | task 過多或過少 | AQE 自動合併；或調整 `spark.sql.shuffle.partitions` |
| **重複計算** | 同一段邏輯被跑很多次 | 多次使用的 DataFrame 用 `.cache()`，用完 `.unpersist()` |
| **Python UDF 慢** | CPU 高、資料在 JVM 和 Python 間搬 | 優先用內建 `F.*` 函式；不得已再用 Pandas UDF（向量化） |

```python
from pyspark.sql.functions import broadcast
big_df.join(broadcast(small_df), "key")
```

**Spark UI 看什麼：**
1. **Jobs / Stages**：哪個 stage 最久？
2. **Stage 詳細頁**：task 時間的 Max 和 Median 差很多 → skew
3. **Shuffle Read / Write**：shuffle 量大 → 想辦法減少 wide transformation 或先 filter
4. **Spill (Memory/Disk)**：有 spill → partition 太大或記憶體不足

---

## 第 4 課：Databricks 平台與 Delta Lake

### 4.1 Databricks 是什麼？

Databricks = **託管的 Spark** + **Delta Lake 儲存格式** + **治理（Unity Catalog）** + **排程、SQL、ML/AI 工具**，整合成「Lakehouse」平台。

```
            ┌───────────────── Unity Catalog（權限、血緣、資料目錄）─────────────────┐
            │                                                                        │
  資料來源 ─▶ Bronze（原始）──▶ Silver（清洗、去重）──▶ Gold（商業彙總）──▶ BI / ML / AI
            │      Delta Lake 表格，存在雲端物件儲存（S3 / ADLS / GCS）               │
            └────────────────────────────────────────────────────────────────────────┘
```

**Unity Catalog 三層命名：** `catalog.schema.table`，例如 `main.sales.orders`。

### 4.2 Delta Lake 核心功能

```python
# 寫成 Delta 表
orders.write.mode("overwrite").saveAsTable("main.learn.orders")

# MERGE：upsert（DE 日常最常用）
spark.sql("""
MERGE INTO main.learn.orders AS t
USING updates AS s
ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")

# Time Travel：查舊版本、救回誤刪資料
spark.sql("DESCRIBE HISTORY main.learn.orders").show()
spark.sql("SELECT * FROM main.learn.orders VERSION AS OF 0").show()
spark.sql("RESTORE TABLE main.learn.orders TO VERSION AS OF 0")

# 維護
spark.sql("OPTIMIZE main.learn.orders")            # 合併小檔案
spark.sql("ALTER TABLE main.learn.orders CLUSTER BY (customer_id)")  # Liquid Clustering
```

| 功能 | 解決什麼問題 |
|---|---|
| ACID 交易 | 寫到一半失敗不會留下壞資料 |
| Schema enforcement / evolution | 擋掉格式不對的資料；需要時可自動加欄位 |
| Time Travel | 回溯、稽核、重跑 |
| Liquid Clustering | 取代傳統 partition + Z-ORDER，查詢自動跳過不相關的檔案 |

### 4.3 增量讀取：Auto Loader

```python
(spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/Volumes/main/learn/chk/schema")
    .load("/Volumes/main/learn/raw/orders/")
 .writeStream
    .option("checkpointLocation", "/Volumes/main/learn/chk/bronze")
    .trigger(availableNow=True)          # 處理完新檔案就停，適合排程批次
    .toTable("main.learn.bronze_orders"))
```

### 4.4 Lakeflow Declarative Pipelines（舊名 DLT）

用宣告式寫法定義整條管線，Databricks 自動處理相依、重試、資料品質檢查：

```sql
CREATE OR REFRESH STREAMING TABLE bronze_orders
AS SELECT * FROM STREAM read_files('/Volumes/main/learn/raw/orders/', format => 'json');

CREATE OR REFRESH STREAMING TABLE silver_orders (
  CONSTRAINT valid_amount EXPECT (amount > 0) ON VIOLATION DROP ROW
)
AS SELECT order_id, customer_id, CAST(order_date AS DATE) AS order_date, amount
FROM STREAM bronze_orders;

CREATE OR REFRESH MATERIALIZED VIEW gold_daily_revenue
AS SELECT order_date, SUM(amount) AS revenue FROM silver_orders GROUP BY order_date;
```

### 4.5 往 AI Engineer 延伸

| 工具 | 用途 |
|---|---|
| **MLflow** | 實驗追蹤、模型版本、GenAI 的 tracing 與評估 |
| **Vector Search** | 把 Delta 表自動同步成向量索引，做 RAG |
| **Model Serving** | 部署模型或 Agent 成 API；也能呼叫外部 LLM |
| **Agent 開發工具** | 在 Databricks 上建、評估、部署 AI Agent |
| **Genie** | 用自然語言查資料表（text-to-SQL） |

> 你的 DE 背景在這裡是優勢：RAG 和 Agent 的品質很大部分取決於資料管線做得好不好。

---

## 期末專案

**題目：把這個 repo 的台股日報資料做成 Lakehouse**

1. **Bronze**：把 `reports/*-picks.csv` 上傳到 Unity Catalog Volume，用 Auto Loader 讀進來
2. **Silver**：統一欄位型別、去除重複、加上 `report_date`
3. **Gold**：
   - 每支股票被選入的次數與平均評分
   - 每日入選檔數趨勢
4. **排程**：用 Lakeflow Jobs 每天跑一次
5. **呈現**：用 Databricks SQL 做一個 Dashboard
6. **加分（AI）**：用 Genie 讓自己能問「這週最常入選的半導體股是哪幾支？」

---

## 面試常考題

1. Transformation 和 Action 的差別？什麼是 lazy evaluation？
2. Narrow vs Wide transformation？什麼時候會 shuffle？
3. `repartition` 和 `coalesce` 差在哪？（前者會 shuffle、可增可減；後者只能減少、盡量不 shuffle）
4. 怎麼處理 data skew？
5. Broadcast join 的原理和使用時機？
6. `cache()` 和 `persist()` 差在哪？
7. 什麼是 AQE（Adaptive Query Execution）？它做了哪三件事？（合併 shuffle partition、切換 join 策略、處理 skew join）
8. Delta Lake 怎麼做到 ACID？（transaction log：`_delta_log/`）
9. Managed table 和 External table 差在哪？
10. Medallion 架構每一層的責任？

---

## 附錄：本機跑 PySpark

```bash
pip install pyspark   # 需要 Java 17 以上
```

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("learn")
         .master("local[*]")
         .getOrCreate())

# Spark UI：http://localhost:4040
```

> Databricks notebook 裡 `spark` 已經建好，不用這段。
