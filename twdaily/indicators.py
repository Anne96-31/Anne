"""技術指標計算（台灣看盤軟體慣用命名：DIF / MACD(DEM) / OSC）。"""
import pandas as pd


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """回傳 (DIF, DEM, OSC)。OSC = DIF - DEM，即柱狀體；OSC 由負轉正即「MACD 翻紅」。"""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dem = dif.ewm(span=signal, adjust=False).mean()
    return dif, dem, dif - dem


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    return (100 - 100 / (1 + rs)).fillna(100)
