"""每日 AI & Data 產業摘要 → Notion。"""

# 本機（Windows）的 Python CA 憑證鏈不完整，requests/certifi 會對部分網站
# 拋 CERTIFICATE_VERIFY_FAILED。truststore 讓它改用作業系統的憑證庫。
# GitHub Actions 的 Ubuntu 不需要，所以裝不到也不報錯。
try:
    import truststore

    truststore.inject_into_ssl()
except Exception:  # pragma: no cover
    pass
