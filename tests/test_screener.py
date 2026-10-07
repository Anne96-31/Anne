import numpy as np
import pandas as pd

from twdaily.indicators import macd
from twdaily.screener import ScreenConfig, evaluate


def _frame(close, volume=5_000_000):
    idx = pd.bdate_range("2026-01-01", periods=len(close))
    return pd.DataFrame({"Close": close, "Volume": volume}, index=idx)


def _find_rebound_series():
    """長期下跌後反彈，找到 OSC 剛在最後一根翻紅的位置。"""
    down = 100 - 40 * np.linspace(0, 1, 110) ** 2  # 加速下跌
    up = np.linspace(60, 75, 40)
    full = np.concatenate([down, up])
    _, _, osc = macd(pd.Series(full))
    for i in range(111, len(full)):
        if osc.iloc[i] > 0 and osc.iloc[i - 1] <= 0:
            return full[: i + 1]
    raise AssertionError("no cross found")


def test_low_level_golden_cross_detected():
    res = evaluate(_frame(_find_rebound_series()))
    assert res is not None
    assert "低檔金叉" in res["signals"]
    assert res["range_pos"] <= 50


def test_steady_uptrend_not_selected():
    assert evaluate(_frame(np.linspace(50, 100, 150))) is None


def test_illiquid_stock_filtered():
    res = evaluate(_frame(_find_rebound_series(), volume=100), ScreenConfig())
    assert res is None


def test_too_short_history():
    assert evaluate(_frame(np.linspace(60, 50, 40))) is None
