# 第 3 課：效能調校入門

> 🎯 學習目標：認得最常見的五種效能問題，並會用 Spark UI 找出慢在哪裡。

## 1. 調校的兩個原則

- **減少 shuffle**：能先 filter 就先 filter，小表用 broadcast
- **讓 partition 大小平均**：避免少數 task 拖慢整個 stage

## 2. 五種常見問題

| 問題 | Spark UI 上的症狀 | 解法 |
|---|---|---|
| 資料傾斜（skew） | 少數幾個 task 跑特別久 | 開 AQE skew join（Databricks 預設開）、對熱門 key 加 salt |
| 太多小檔案 | 讀取慢、task 數量爆多 | Delta 的 OPTIMIZE、寫出前 coalesce |
| 大表 join 小表很慢 | 計畫出現 SortMergeJoin | 用 broadcast 強制廣播小表 |
| Shuffle partition 數不合適 | task 太多（每個很小）或太少（每個很大） | 讓 AQE 自動合併；或調整 spark.sql.shuffle.partitions |
| Python UDF 太慢 | CPU 很高、資料在 JVM 和 Python 間來回 | 優先用內建 F.* 函式；不得已再用 Pandas UDF |

## 3. Broadcast Join

小表複製一份給每個 Executor，大表就不用 shuffle。

```python
from pyspark.sql.functions import broadcast

orders.join(broadcast(countries), "country_code")
```

- Spark 會自動廣播小於 `spark.sql.autoBroadcastJoinThreshold`（預設 10 MB）的表
- AQE 執行時發現某一邊很小，也會自動改成 broadcast

> ⚠️ 地雷：不要廣播太大的表（例如好幾 GB），Driver 和每個 Executor 都要放一份，會 OOM。

## 4. 資料傾斜與 Salting

如果 90% 的訂單都來自同一個客戶，那個 key 的 task 會比別人慢非常多。Salting 的做法是把熱門 key 拆成幾份：

```python
from pyspark.sql import functions as F

N = 8
big = big.withColumn("salt", (F.rand() * N).cast("int"))
small = small.crossJoin(spark.range(N).withColumnRenamed("id", "salt"))
big.join(small, ["customer_id", "salt"])
```

> 💡 在 Databricks 上先確認 AQE 開著（`spark.sql.adaptive.enabled`），大多數傾斜它會自動處理，真的不夠再手動 salt。

## 5. repartition vs coalesce

| | repartition(n) | coalesce(n) |
|---|---|---|
| 會 shuffle 嗎 | 會 | 盡量不會 |
| 可以增加 partition 嗎 | 可以 | 只能減少 |
| 資料分布 | 平均 | 可能不平均 |
| 適合 | 平行度不夠、要依欄位重新分區 | 寫出前減少檔案數 |

## 6. 快取（cache）

同一個 DataFrame 會被用好幾次時，可以先快取，避免重複計算：

```python
features = expensive_df.cache()
features.count()          # 用一個 action 觸發快取
model_a = features.filter(...)
model_b = features.groupBy(...)
features.unpersist()      # 用完記得釋放
```

- `cache()` = `persist()` 用預設的儲存層級
- `persist()` 可以指定 MEMORY_ONLY、MEMORY_AND_DISK 等層級

## 7. 用 Spark UI 找問題

1. **Jobs / Stages**：哪個 stage 最久？
2. **Stage 詳細頁**：task 時間的 Max 遠大於 Median → 資料傾斜
3. **Shuffle Read / Write**：量很大 → 減少 wide transformation 或先 filter
4. **Spill（Memory / Disk）**：有 spill → partition 太大或記憶體不夠
5. **SQL / DataFrame 頁籤**：看實際執行的計畫，確認 join 類型

## 8. 重點整理

- 先看 Spark UI 找出慢的 stage，再決定怎麼調
- 小表 broadcast、傾斜先靠 AQE、不夠再 salt
- 減少檔案數用 coalesce，重新平均分區用 repartition
- 重複使用才 cache，用完 unpersist
- 能用內建函式就不要寫 Python UDF

## 9. 練習

1. 某個 stage 有 200 個 task，Median 3 秒，Max 8 分鐘，最可能是什麼問題？怎麼處理？
2. 每天寫出 5,000 個 1 MB 的小檔案，下游讀取很慢，有哪兩種改善方式？
3. `repartition(1)` 和 `coalesce(1)` 都能寫出單一檔案，差在哪？

<details>
<summary>參考答案</summary>

1. 資料傾斜：少數 key 的資料特別多。先確認 AQE 和 skew join 有開；不夠的話，對熱門 key 做 salting。
2. 寫出前用 `coalesce` 減少檔案數；寫成 Delta 表後定期跑 `OPTIMIZE` 合併小檔案（Databricks 也可以開 auto optimize）。
3. `repartition(1)` 會先 shuffle，前面的運算仍然平行；`coalesce(1)` 不 shuffle，但可能讓前面整段運算都擠在一個 task 裡跑，反而更慢。資料量大時通常 `repartition(1)` 比較好。

</details>
