"""NOL World 餘票追蹤：定時重新整理購票頁，畫面一有變化就用 Telegram 通知。

只做「看」和「通知」，不會自動下單。請在自己的電腦上執行（見 README.md）。

指令：
  python watch.py telegram   設定 Telegram bot，並送一則測試訊息
  python watch.py setup      開瀏覽器讓你登入，停在「售完」的畫面後按 Enter，記下基準畫面
  python watch.py check      只檢查一次，把結果和截圖印出來（測試用）
  python watch.py run        持續追蹤，預設每 90 秒左右檢查一次
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from playwright.sync_api import BrowserContext, Page, sync_playwright

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"
PROFILE = HERE / ".browser-profile"  # 登入狀態存在這裡，不會上傳
SHOTS = HERE / "screenshots"

DEFAULT_URL = "https://world.nol.com/en/ticket/products/26015024"  # 米津玄師 GHOST 仁川場
MIN_INTERVAL = 60  # 秒；不要再調低，避免對售票網站造成負擔或被封鎖

SOLD_OUT_WORDS = ["sold out", "soldout", "매진", "no seats", "not available", "售完", "完売"]
AVAILABLE_WORDS = ["remaining", "seats left", "잔여", "available seat", "select seat", "좌석선택", "残り", "剩餘"]

# 會一直變動、與餘票無關的文字（倒數計時、時鐘等），比對前先拿掉
NOISE = [re.compile(p, re.I) for p in [r"\b\d{1,2}:\d{2}(:\d{2})?\b", r"likes \(\d+\)", r"usd [\d.,]+~?"]]


# ---------------------------------------------------------------- 設定檔
def load_config() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {}


def save_config(cfg: dict) -> None:
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def log(msg: str) -> None:
    print(f"[{datetime.now():%m-%d %H:%M:%S}] {msg}", flush=True)


# ---------------------------------------------------------------- Telegram
def tg_send(cfg: dict, text: str, photo: Path | None = None) -> bool:
    token, chat = cfg.get("telegram_token"), cfg.get("telegram_chat_id")
    if not token or not chat:
        log("（尚未設定 Telegram，只印在畫面上）\n" + text)
        return False
    base = f"https://api.telegram.org/bot{token}"
    try:
        if photo and photo.exists():
            with photo.open("rb") as f:
                r = requests.post(f"{base}/sendPhoto", data={"chat_id": chat, "caption": text[:1000]},
                                  files={"photo": f}, timeout=30)
        else:
            r = requests.post(f"{base}/sendMessage", data={"chat_id": chat, "text": text[:4000]}, timeout=30)
        if not r.ok:
            log(f"Telegram 傳送失敗：{r.status_code} {r.text[:200]}")
        return r.ok
    except requests.RequestException as e:
        log(f"Telegram 連線失敗：{e}")
        return False


def cmd_telegram(_args) -> None:
    cfg = load_config()
    print("1. 在 Telegram 搜尋 @BotFather，傳 /newbot，照指示取名字，最後會拿到一串 token。")
    token = input("2. 把 token 貼在這裡：").strip()
    print("3. 在 Telegram 打開你剛建立的 bot，按「開始」或傳任何一句話給它。")
    input("   傳完之後按 Enter…")
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30).json()
    chats = [u["message"]["chat"]["id"] for u in r.get("result", []) if "message" in u]
    if not chats:
        sys.exit("找不到你的訊息。確認 token 正確、而且有先傳訊息給 bot，再執行一次。")
    cfg.update(telegram_token=token, telegram_chat_id=chats[-1])
    save_config(cfg)
    ok = tg_send(cfg, "✅ 米津玄師餘票追蹤：Telegram 通知設定成功！")
    print("設定完成，手機應該收到測試訊息了。" if ok else "設定已存，但測試訊息沒送出，請檢查 token。")


# ---------------------------------------------------------------- 瀏覽器
def open_context(pw, headless: bool) -> BrowserContext:
    kwargs = dict(headless=headless, locale="en-US", viewport={"width": 1280, "height": 900})
    if os.environ.get("CHROMIUM_PATH"):
        kwargs["executable_path"] = os.environ["CHROMIUM_PATH"]
    return pw.chromium.launch_persistent_context(str(PROFILE), **kwargs)


def is_login_page(page: Page) -> bool:
    return "/login" in page.url or "auth-web" in page.url


def load_watch_page(ctx: BrowserContext, cfg: dict) -> Page:
    """打開要追蹤的頁面；若停在商品頁就自動按 Buy now，進到選日期／座位的畫面。"""
    for extra in ctx.pages[1:]:
        extra.close()
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    url = cfg.get("watch_url") or DEFAULT_URL
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_timeout(6_000)

    if cfg.get("click_buy_now", True) and "/ticket/products/" in page.url and not is_login_page(page):
        btn = page.get_by_text(re.compile(r"^(Buy now|예매하기|購買)$", re.I)).first
        if btn.count():
            try:
                with ctx.expect_page(timeout=10_000) as popup:
                    btn.click(timeout=10_000)
                page = popup.value  # 購票畫面開在新視窗
            except Exception:
                pass  # 沒開新視窗，就是同一頁裡的視窗或換頁
            page.wait_for_timeout(8_000)
    return page


def snapshot(page: Page, tag: str) -> tuple[str, Path]:
    SHOTS.mkdir(exist_ok=True)
    shot = SHOTS / f"{datetime.now():%Y%m%d-%H%M%S}-{tag}.png"
    page.screenshot(path=str(shot), full_page=True)
    texts = []
    for frame in page.frames:  # 座位選擇常放在 iframe 裡
        try:
            texts.append(frame.locator("body").inner_text(timeout=5_000))
        except Exception:
            pass
    return "\n".join(texts), shot


def normalize(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = " ".join(line.split())
        for pat in NOISE:
            line = pat.sub("", line)
        if line.strip():
            lines.append(line.strip())
    return lines


def count_words(lines: list[str], words: list[str]) -> int:
    blob = "\n".join(lines).lower()
    return sum(blob.count(w) for w in words)


# ---------------------------------------------------------------- 指令
def cmd_setup(_args) -> None:
    cfg = load_config()
    with sync_playwright() as pw:
        ctx = open_context(pw, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(DEFAULT_URL, wait_until="domcontentloaded")
        print("\n瀏覽器已經打開：")
        print("  1. 右上角 Sign in，用你的 NOL World 帳號登入")
        print("  2. 回到演唱會頁面，按 Buy now，一路點到能看到「哪些日期／座位等級售完」的畫面")
        print("  3. 停在那個畫面，不要關瀏覽器")
        input("完成後回到這裡按 Enter…")
        current = ctx.pages[-1]
        cfg["watch_url"] = current.url
        # 若最後停在購票彈出視窗，追蹤時還是從商品頁進去比較穩
        if "/ticket/products/" not in current.url:
            print(f"記下的網址：{current.url}")
        text, shot = snapshot(current, "baseline")
        lines = normalize(text)
        cfg["baseline"] = lines
        save_config(cfg)
        ctx.close()
    print(f"\n已記下基準畫面（{len(lines)} 行文字），截圖：{shot}")
    print(f"其中「售完」字樣 {count_words(lines, SOLD_OUT_WORDS)} 處。接下來可以先執行 `python watch.py check` 測試。")


def evaluate(cfg: dict, lines: list[str]) -> tuple[str, list[str]]:
    """回傳 (狀態, 新出現的文字行)。狀態：same / changed / likely_available。"""
    base = cfg.get("baseline") or []
    new_lines = [l[2:] for l in difflib.ndiff(base, lines) if l.startswith("+ ")]
    if not new_lines and len(lines) == len(base):
        return "same", []
    sold_now, sold_before = count_words(lines, SOLD_OUT_WORDS), count_words(base, SOLD_OUT_WORDS)
    if count_words(new_lines, AVAILABLE_WORDS) or (sold_before and sold_now < sold_before):
        return "likely_available", new_lines
    return "changed", new_lines


def check_once(ctx: BrowserContext, cfg: dict, state: dict) -> None:
    page = load_watch_page(ctx, cfg)
    if is_login_page(page):
        if time.time() - state.get("login_alert", 0) > 3600:
            tg_send(cfg, "⚠️ 餘票追蹤：NOL World 登入過期了，請在電腦上重新執行 `python watch.py setup` 登入。")
            state["login_alert"] = time.time()
        log("登入過期，等待重新登入")
        return
    text, shot = snapshot(page, "check")
    lines = normalize(text)
    status, new_lines = evaluate(cfg, lines)
    digest = hashlib.sha1("\n".join(lines).encode()).hexdigest()

    if status == "same":
        shot.unlink(missing_ok=True)  # 沒變化就不留截圖
        log("沒有變化（仍售完）")
    elif digest == state.get("last_digest"):
        shot.unlink(missing_ok=True)
        log(f"{status}，但和上次通知的畫面相同，不重複通知")
    else:
        head = "🎫 可能有餘票！快去搶" if status == "likely_available" else "👀 購票畫面有變化，請看一下"
        detail = "\n".join(new_lines[:15]) or "（文字行數改變）"
        tg_send(cfg, f"{head}\n{page.url}\n\n新出現的內容：\n{detail}", shot)
        log(f"{status}：已通知。新內容：{new_lines[:5]}")
        state["last_digest"] = digest


def cmd_check(args) -> None:
    cfg = load_config()
    with sync_playwright() as pw:
        ctx = open_context(pw, headless=not args.show)
        check_once(ctx, cfg, {})
        ctx.close()


def cmd_run(args) -> None:
    cfg = load_config()
    if not cfg.get("baseline"):
        sys.exit("還沒有基準畫面，請先執行 `python watch.py setup`。")
    interval = max(MIN_INTERVAL, args.interval)
    tg_send(cfg, f"▶️ 餘票追蹤開始，每 {interval} 秒左右檢查一次。")
    state: dict = {}
    errors = 0
    with sync_playwright() as pw:
        ctx = open_context(pw, headless=not args.show)
        try:
            while True:
                try:
                    check_once(ctx, cfg, state)
                    errors = 0
                except Exception as e:  # 網路斷線、頁面逾時等
                    errors += 1
                    log(f"檢查失敗（第 {errors} 次）：{e}")
                    if errors == 5:
                        tg_send(cfg, f"⚠️ 餘票追蹤連續失敗 5 次，最後的錯誤：{str(e)[:300]}")
                time.sleep(interval * random.uniform(0.8, 1.2))
        except KeyboardInterrupt:
            log("已停止")
        finally:
            ctx.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="NOL World 餘票追蹤")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("telegram", help="設定 Telegram 通知").set_defaults(func=cmd_telegram)
    sub.add_parser("setup", help="登入並記下售完時的基準畫面").set_defaults(func=cmd_setup)
    c = sub.add_parser("check", help="只檢查一次")
    c.add_argument("--show", action="store_true", help="顯示瀏覽器視窗")
    c.set_defaults(func=cmd_check)
    r = sub.add_parser("run", help="持續追蹤")
    r.add_argument("--interval", type=int, default=90, help=f"檢查間隔秒數（最少 {MIN_INTERVAL}）")
    r.add_argument("--show", action="store_true", help="顯示瀏覽器視窗")
    r.set_defaults(func=cmd_run)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
