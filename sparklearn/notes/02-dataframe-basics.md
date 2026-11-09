# 第 2 課：DataFrame 實戰

> 🎯 學習目標：熟悉 DataFrame 最常用的操作（select、filter、groupBy、join、window），並學會用 `explain()` 看執行計畫。

## 1. 準備環境

- **Databricks notebook**：`spark` 已經建好，直接用
- **本機**：`pip install pyspark`（需要 Java 17 以上），再建立 SparkSession

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("learn")
         .master("local[*]")
         .getOrCreate())
# Spark UI：http://localhost:4040
```

## 2. 建立練習資料

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

## 3. 常用操作

| 想做的事 | PySpark | SQL |
|---|---|---|
| 選欄位 | `df.select("a", "b")` | SELECT a, b |
| 新增欄位 | `df.withColumn("x", F.col("a") * 2)` | SELECT *, a * 2 AS x |
| 篩選 | `df.filter(F.col("a") > 1)` | WHERE a > 1 |
| 分組聚合 | `df.groupBy("k").agg(F.sum("v"))` | GROUP BY k |
| 合併 | `df.join(other, "k", "left")` | LEFT JOIN |
| 條件欄位 | `F.when(cond, x).otherwise(y)` | CASE WHEN |
| 排序 | `df.orderBy(F.desc("v"))` | ORDER BY v DESC |

```python
# 篩選 + 新增欄位
orders.filter((F.col("country") == "TW") & (F.col("amount") > 500)) \
      .withColumn("amount_twd", F.col("amount") * 32)

# 分組聚合
orders.groupBy("country").agg(
    F.count("*").alias("n_orders"),
    F.sum("amount").alias("revenue"),
    F.round(F.avg("amount"), 1).alias("avg_amount"),
).show()

# Join + 條件欄位
orders.join(customers, on="customer_id", how="left") \
      .withColumn("size", F.when(F.col("amount") >= 1000, "big").otherwise("small"))
```

同一件事用 SQL 寫：

```python
orders.createOrReplaceTempView("orders")
spark.sql("""
    SELECT country, COUNT(*) AS n_orders, SUM(amount) AS revenue
    FROM orders
    GROUP BY country
""").show()
```

> 💡 DataFrame API 和 Spark SQL 底層用同一個優化器，效能一樣，選順手的寫就好。

> ⚠️ 地雷：條件要用 `&`、`|`、`~`，不能用 Python 的 `and`、`or`、`not`，而且每個條件都要加括號。

## 4. Window Function（面試必考）

Window function 讓你「分組計算，但不把列合併」。例如每位客戶的第幾筆訂單、累計消費、上一筆金額：

```python
w = Window.partitionBy("customer_id").orderBy("order_date")

orders.withColumn("order_seq", F.row_number().over(w)) \
      .withColumn("running_total", F.sum("amount").over(w)) \
      .withColumn("prev_amount", F.lag("amount").over(w)) \
      .orderBy("customer_id", "order_date") \
      .show()
```

| 函式 | 用途 |
|---|---|
| row_number | 1, 2, 3…（不重複） |
| rank / dense_rank | 同分同名次（rank 會跳號，dense_rank 不跳） |
| lag / lead | 上一列 / 下一列的值 |
| sum / avg ... over(w) | 累計、移動平均 |

> ⚠️ 地雷：`Window.orderBy(...)` 不加 `partitionBy` 時，所有資料會集中到一個 partition，只適合小資料。

## 5. 看執行計畫

```python
orders.join(customers, "customer_id").groupBy("tier").sum("amount").explain("formatted")
```

在輸出裡找這些關鍵字：

- **Exchange**：這裡發生 shuffle
- **BroadcastHashJoin**：小表被廣播，不用 shuffle（好事）
- **SortMergeJoin**：兩邊都 shuffle 再排序（大表 join 大表）
- **AdaptiveSparkPlan**：AQE 開著，執行時可能再改計畫

## 6. 重點整理

- 常用操作：select、withColumn、filter、groupBy().agg()、join、when
- DataFrame API 和 SQL 效能相同
- Window function = 分組計算但保留每一列
- `explain()` 看 Exchange 就知道哪裡有 shuffle

## 7. 練習

1. 算出每個 `tier` 的總營收與訂單數。
2. 找出每位客戶金額最大的那一筆訂單。
3. 算每天的營收，以及跟前一天相比的成長率。
4. 對第 1 題呼叫 `.explain()`，看看是哪一種 join。

<details>
<summary>參考答案</summary>

```python
# 1
orders.join(customers, "customer_id") \
      .groupBy("tier") \
      .agg(F.sum("amount").alias("revenue"), F.count("*").alias("n_orders")) \
      .show()
# Gold 7450.0 / 4 筆，Silver 1800.0 / 2 筆

# 2
w2 = Window.partitionBy("customer_id").orderBy(F.desc("amount"))
orders.withColumn("rk", F.row_number().over(w2)).filter("rk = 1").drop("rk").show()

# 3
daily = orders.groupBy("order_date").agg(F.sum("amount").alias("revenue"))
w3 = Window.orderBy("order_date")
daily.withColumn("prev", F.lag("revenue").over(w3)) \
     .withColumn("growth_pct", F.round((F.col("revenue") / F.col("prev") - 1) * 100, 1)) \
     .show()
# 11/02 成長 286.7%，11/03 成長 -66.4%

# 4：explain() 顯示的是執行前的計畫，可能是 SortMergeJoin，
#    外層的 AdaptiveSparkPlan 代表 AQE 執行時可能改成 broadcast。
#    想確定用 broadcast 就自己指定，這時會看到 BroadcastHashJoin：
orders.join(F.broadcast(customers), "customer_id").groupBy("tier").sum("amount").explain()
```

</details>
