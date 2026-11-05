"""設定：全部來自環境變數（GitHub Actions 用 secrets，本機可用 .env）。"""

from __future__ import annotations

import os
from datetime import timezone, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TPE = ZoneInfo("Asia/Taipei")
except Exception:                                   # 沒有 tzdata 時退回固定偏移
    TPE = timezone(timedelta(hours=8))

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "digests"
STATE_FILE = OUT_DIR / "state.json"
ENV_FILE = BASE_DIR / ".env"


def load_env(path: Path = ENV_FILE) -> None:
    """本機開發用：把 .env 讀進 os.environ（不覆蓋既有環境變數）。CI 上不存在此檔。"""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def get_int(name: str, default: int) -> int:
    try:
        return int(get(name) or default)
    except ValueError:
        return default


load_env()

# --- Notion ---
NOTION_TOKEN = get("NOTION_TOKEN")
# 母頁底下每天開一個子頁。沿用 repo 既有命名慣例（NOTION_ENGLISH_DATABASE_ID 之類）
NOTION_PAGE_ID = get("NOTION_AI_DIGEST_PAGE_ID") or get("NOTION_PARENT_PAGE_ID")
NOTION_VERSION = "2022-06-28"

# --- Claude ---
ANTHROPIC_API_KEY = get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = get("ANTHROPIC_MODEL", "claude-opus-5")
ANTHROPIC_EFFORT = get("ANTHROPIC_EFFORT", "medium")   # low / medium / high / xhigh / max

# --- 內容 ---
LOOKBACK_DAYS = get_int("DIGEST_LOOKBACK_DAYS", 2)
MAX_ITEMS = get_int("DIGEST_MAX_ITEMS", 14)
MAX_PER_SOURCE = get_int("DIGEST_MAX_PER_SOURCE", 4)
HTTP_TIMEOUT = get_int("DIGEST_HTTP_TIMEOUT", 25)

# Notion 頁面與 digests/ 檔案的保存天數（workflow 用 RETENTION_DAYS 傳入）
RETENTION_DAYS = get_int("RETENTION_DAYS", 30)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 aidigest/2.0"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}
