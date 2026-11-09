# 第 4 課：Databricks 平台與 Delta Lake

> 🎯 學習目標：了解 Databricks Lakehouse 的組成，會用 Delta Lake 做 MERGE、Time Travel，並看懂一條 Bronze → Silver → Gold 管線。

## 1. Databricks 是什麼？

Databricks = **託管的 Spark** + **Delta Lake 儲存格式** + **Unity Catalog 治理** + **排程、SQL、ML/AI 工具**，整合成「Lakehouse」平台。

```text
        ┌─────────── Unity Catalog（權限、血緣、資料目錄）───────────┐
        │                                                            │
資料來源 ─▶ Bronze（原始）─▶ Silver（清洗、去重）─▶ Gold（商業彙總）─▶ BI / ML / AI
        │   Delta Lake 表格，存在雲端物件儲存（S3 / ADLS / GCS）      │
        └────────────────────────────────────────────────────────────┘
```

| 元件 | 用途 |
|---|---|
| Workspace / Notebook | 寫程式、協作 |
| Compute（Cluster / Serverless） | 執行運算 |
| Unity Catalog | 管理資料表、權限、血緣；三層命名 catalog.schema.table |
| Volumes | 存放非表格檔案（CSV、JSON、圖片） |
| Lakeflow Jobs | 排程與工作流程 |
| Databricks SQL | SQL 查詢與 Dashboard |

> 💡 免費練習：Databricks Free Edition 有 Serverless、Unity Catalog 和 SQL，足夠做完本課所有練習。

## 2. Medallion 架構

| 層 | 內容 | 原則 |
|---|---|---|
| Bronze | 原始資料，照原樣存 | 只新增、不修改，保留重跑能力 |
| Silver | 清洗、型別轉換、去重、join | 一筆資料一個真實版本 |
| Gold | 依商業需求彙總 | 給報表、Dashboard、ML 直接用 |

## 3. Delta Lake 核心功能

| 功能 | 解決什麼問題 |
|---|---|
| ACID 交易 | 寫到一半失敗不會留下壞資料（靠 _delta_log 交易紀錄） |
| Schema enforcement / evolution | 擋掉格式不對的資料；需要時可自動加欄位 |
| Time Travel | 查舊版本、稽核、救回誤刪資料 |
| MERGE | 一個指令完成 upsert |
| Liquid Clustering | 取代傳統 partition + Z-ORDER，查詢自動跳過不相關檔案 |

```python
# 寫成 Delta 表（Databricks 預設格式就是 Delta）
orders.write.mode("overwrite").saveAsTable("main.learn.orders")
```

### MERGE（DE 日常最常用）

```sql
MERGE INTO main.learn.orders AS t
USING updates AS s
ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

### Time Travel

```sql
DESCRIBE HISTORY main.learn.orders;
SELECT * FROM main.learn.orders VERSION AS OF 0;
RESTORE TABLE main.learn.orders TO VERSION AS OF 0;
```

### 維護

```sql
OPTIMIZE main.learn.orders;                          -- 合併小檔案
ALTER TABLE main.learn.orders CLUSTER BY (customer_id);  -- Liquid Clustering
VACUUM main.learn.orders;                            -- 清掉不再需要的舊檔案（預設保留 7 天）
```

> ⚠️ 地雷：VACUUM 之後，被清掉的舊版本就不能再 Time Travel 了。

## 4. Managed vs External Table

| | Managed table | External table |
|---|---|---|
| 檔案位置 | 由 Unity Catalog 管理 | 你指定的雲端路徑 |
| DROP TABLE 時 | 資料一起刪 | 只刪定義，檔案還在 |
| 建議 | 預設用這個 | 資料要給其他系統共用時 |

## 5. 增量讀取：Auto Loader

自動偵測資料夾裡的新檔案，只處理還沒處理過的：

```python
(spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/Volumes/main/learn/chk/schema")
    .load("/Volumes/main/learn/raw/orders/")
 .writeStream
    .option("checkpointLocation", "/Volumes/main/learn/chk/bronze")
    .trigger(availableNow=True)      # 處理完新檔案就停，適合排程批次
    .toTable("main.learn.bronze_orders"))
```

- **checkpoint** 記錄處理到哪裡，重跑不會重複
- `availableNow=True` 讓串流程式也能當批次排程用

## 6. Lakeflow Declarative Pipelines（舊名 DLT）

用宣告式寫法定義整條管線，Databricks 自動處理相依關係、重試和資料品質：

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

- **Streaming table**：增量處理新資料
- **Materialized view**：結果預先算好，自動更新
- **Expectations**：資料品質規則（警告、丟棄或讓管線失敗）

## 7. 往 AI Engineer 延伸

| 工具 | 用途 |
|---|---|
| MLflow | 實驗追蹤、模型版本、GenAI 的 tracing 與評估 |
| Vector Search | 把 Delta 表同步成向量索引，做 RAG |
| Model Serving | 把模型或 Agent 部署成 API；也能呼叫外部 LLM |
| Agent 開發工具 | 在 Databricks 上建置、評估、部署 AI Agent |
| Genie | 用自然語言查資料表（text-to-SQL） |

> 💡 DE 背景是優勢：RAG 和 Agent 的品質，很大部分取決於資料管線做得好不好。

## 8. 重點整理

- Databricks = Spark + Delta Lake + Unity Catalog + 排程 / SQL / AI
- Medallion：Bronze 原始、Silver 清洗、Gold 彙總
- Delta Lake 靠 _delta_log 做到 ACID、Time Travel、MERGE
- Auto Loader + checkpoint 做增量匯入；Lakeflow 管線用宣告式寫法

## 9. 練習

1. 在 Free Edition 建一個 schema `main.learn`，把第 2 課的 `orders` 寫成 Delta 表。
2. 建一個 `updates` DataFrame：修改 order_id 3 的金額，並新增 order_id 7，用 MERGE 寫回去。
3. 用 `DESCRIBE HISTORY` 看版本，再用 `VERSION AS OF` 查 MERGE 之前的資料。
4. 說說看：為什麼 Bronze 層要保留原始資料、不直接清洗？

<details>
<summary>參考答案</summary>

```python
# 1
spark.sql("CREATE SCHEMA IF NOT EXISTS main.learn")
orders.write.mode("overwrite").saveAsTable("main.learn.orders")

# 2
updates = spark.createDataFrame(
    [(3, "C01", "2026-11-02", "TW", 999.0), (7, "C03", "2026-11-04", "US", 700.0)],
    ["order_id", "customer_id", "order_date", "country", "amount"],
).withColumn("order_date", F.to_date("order_date"))
updates.createOrReplaceTempView("updates")
spark.sql("""
MERGE INTO main.learn.orders t USING updates s ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")

# 3
spark.sql("DESCRIBE HISTORY main.learn.orders").select("version", "operation").show()
spark.sql("SELECT * FROM main.learn.orders VERSION AS OF 0 WHERE order_id = 3").show()
```

4. 清洗邏輯可能有錯或需求會改。保留原始資料，就能隨時從 Bronze 重跑出正確的 Silver / Gold，不用回頭找來源系統要資料，也方便稽核。

</details>
