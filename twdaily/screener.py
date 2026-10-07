"""「從低檔翻揚、MACD 轉正」選股邏輯。

訊號定義（任一成立即入選）：
  A. 低檔金叉：近 N 日內 OSC 由負轉正（DIF 上穿 DEM），且交叉當下 DIF < 0（零軸下方），
     收盤價位於近 120 日區間的下半部（<= 50%）。
  B. DIF 翻正：近 N 日內 DIF 由負轉正（站上零軸），且之前 20 日中至少 10 日 DIF 為負，
     代表由空方格局翻多。
共同條件：最新 OSC 仍 > 0（訊號未失效）、近 20 日平均成交金額 >= 門檻（排除冷門股）。
"""
from dataclasses import dataclass

import pandas as pd

from .indicators import macd, rsi


@dataclass
class ScreenConfig:
    lookback: int = 3                 # 訊號需發生在最近幾根 K 棒內
    range_window: int = 120           # 判斷「低檔」的區間長度
    max_range_position: float = 0.5   # 收盤價在區間中的位置上限（0=最低, 1=最高）
    min_avg_value: float = 3e7        # 近 20 日平均成交金額下限（新台幣）
    min_bars: int = 80


def _last_cross_up(series: pd.Series, lookback: int):
    """最近 lookback 根內 series 由 <=0 轉為 >0 的位置（負索引），找不到回傳 None。"""
    for k in range(1, lookback + 1):
        if series.iloc[-k] > 0 and series.iloc[-k - 1] <= 0:
            return -k
    return None


def evaluate(df: pd.DataFrame, cfg: ScreenConfig = ScreenConfig()):
    """df 需含 Close、Volume 欄位（日線，舊到新）。符合條件回傳 dict，否則 None。"""
    df = df.dropna(subset=["Close"])
    if len(df) < cfg.min_bars:
        return None
    close, volume = df["Close"], df["Volume"].fillna(0)

    avg_value = (close * volume).iloc[-20:].mean()
    if avg_value < cfg.min_avg_value:
        return None

    dif, dem, osc = macd(close)
    if osc.iloc[-1] <= 0:
        return None

    window = close.iloc[-cfg.range_window:]
    lo, hi = window.min(), window.max()
    range_pos = (close.iloc[-1] - lo) / (hi - lo) if hi > lo else 0.0

    signals = []
    gc = _last_cross_up(osc, cfg.lookback)
    if gc is not None and dif.iloc[gc] < 0 and range_pos <= cfg.max_range_position:
        signals.append("低檔金叉")
    zc = _last_cross_up(dif, cfg.lookback)
    if zc is not None and (dif.iloc[zc - 20:zc] < 0).sum() >= 10:
        signals.append("DIF翻正")
    if not signals:
        return None

    ma20 = close.rolling(20).mean().iloc[-1]
    vol_ratio = volume.iloc[-1] / volume.iloc[-21:-1].mean() if volume.iloc[-21:-1].mean() > 0 else 0.0
    rsi14 = rsi(close).iloc[-1]
    osc_rising = osc.iloc[-1] > osc.iloc[-2] > osc.iloc[-3]

    # 評分：訊號強度 + 確認條件，滿分 7
    score = 2 * len(signals)
    score += close.iloc[-1] > ma20
    score += vol_ratio >= 1.5
    score += 40 <= rsi14 <= 65
    score += bool(osc_rising)

    return {
        "date": df.index[-1].strftime("%Y-%m-%d"),
        "close": round(float(close.iloc[-1]), 2),
        "chg_pct": round(float(close.iloc[-1] / close.iloc[-2] - 1) * 100, 2),
        "signals": "+".join(signals),
        "score": int(score),
        "dif": round(float(dif.iloc[-1]), 3),
        "osc": round(float(osc.iloc[-1]), 3),
        "range_pos": round(float(range_pos) * 100, 1),
        "above_ma20": bool(close.iloc[-1] > ma20),
        "vol_ratio": round(float(vol_ratio), 2),
        "rsi14": round(float(rsi14), 1),
        "avg_value_m": round(float(avg_value) / 1e6, 1),
    }
