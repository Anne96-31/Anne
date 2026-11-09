"""資訊來源清單。weight 會直接加進排序分數（越高越優先曝光）。

category 用來在 Notion 上分組顯示：
  core        你指定的必看網站（KDnuggets / TDS / Analytics Vidhya / Uber / TechOrange）
  eng         大廠工程部落格（實戰架構、系統設計）
  lab         模型與平台官方（模型/工具發布）
  practitioner 個人/電子報（AI Engineer 職涯與實作心法）
  research    論文與研究
"""

from __future__ import annotations

# type:
#   "rss"    -> 標準 RSS/Atom
#   "manual" -> 官方沒有 feed，只能人工瀏覽（fetch 時會略過並在 log 提醒）
SOURCES: list[dict] = [
    # ---------- 你指定的核心來源 ----------
    {"key": "kdnuggets", "name": "KDnuggets", "type": "rss",
     "url": "https://www.kdnuggets.com/feed",
     "site": "https://www.kdnuggets.com/", "category": "core", "weight": 3.0},

    {"key": "tds", "name": "Towards Data Science", "type": "rss",
     "url": "https://towardsdatascience.com/feed",
     "site": "https://towardsdatascience.com/", "category": "core", "weight": 3.0},

    {"key": "analyticsvidhya", "name": "Analytics Vidhya", "type": "rss",
     "url": "https://www.analyticsvidhya.com/feed/",
     "site": "https://www.analyticsvidhya.com/", "category": "core", "weight": 2.5},

    {"key": "techorange", "name": "TechOrange 科技報橘", "type": "rss",
     "url": "https://techorange.com/feed/",
     "site": "https://techorange.com/", "category": "core", "weight": 2.6},

    # Uber 已把 eng.uber.com 併入 uber.com/blog/engineering，該頁純前端渲染、
    # 沒有公開 RSS，且 robots.txt 明文 disallow */api/，所以程式不做抓取。
    {"key": "uber_eng", "name": "Uber Engineering Blog", "type": "manual",
     "url": "https://www.uber.com/en-US/blog/engineering/",
     "site": "https://www.uber.com/en-US/blog/engineering/", "category": "core", "weight": 3.0,
     "note": "官方無 RSS（robots.txt 禁止 API 抓取），請人工瀏覽；同性質內容已由 Netflix / Meta / Pinterest / Airbnb 工程部落格補上。"},

    # ---------- 大廠工程部落格（Uber 的替代與加強）----------
    {"key": "netflix", "name": "Netflix TechBlog", "type": "rss",
     "url": "https://netflixtechblog.com/feed",
     "site": "https://netflixtechblog.com/", "category": "eng", "weight": 2.8},

    {"key": "meta_eng", "name": "Engineering at Meta", "type": "rss",
     "url": "https://engineering.fb.com/feed/",
     "site": "https://engineering.fb.com/", "category": "eng", "weight": 2.5},

    {"key": "pinterest_eng", "name": "Pinterest Engineering", "type": "rss",
     "url": "https://medium.com/feed/pinterest-engineering",
     "site": "https://medium.com/@Pinterest_Engineering", "category": "eng", "weight": 2.3},

    {"key": "airbnb_eng", "name": "Airbnb Engineering", "type": "rss",
     "url": "https://medium.com/feed/airbnb-engineering",
     "site": "https://medium.com/airbnb-engineering", "category": "eng", "weight": 2.3},

    {"key": "databricks", "name": "Databricks Blog", "type": "rss",
     "url": "https://www.databricks.com/feed",
     "site": "https://www.databricks.com/blog", "category": "eng", "weight": 2.6},

    {"key": "aws_ml", "name": "AWS Machine Learning Blog", "type": "rss",
     "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
     "site": "https://aws.amazon.com/blogs/machine-learning/", "category": "eng", "weight": 2.2},

    {"key": "cloudflare", "name": "Cloudflare Blog", "type": "rss",
     "url": "https://blog.cloudflare.com/rss/",
     "site": "https://blog.cloudflare.com/", "category": "eng", "weight": 1.6},

    {"key": "github_ai", "name": "GitHub Blog – AI & ML", "type": "rss",
     "url": "https://github.blog/ai-and-ml/feed/",
     "site": "https://github.blog/ai-and-ml/", "category": "eng", "weight": 1.8},

    # ---------- 模型 / 平台官方 ----------
    {"key": "openai", "name": "OpenAI News", "type": "rss",
     "url": "https://openai.com/news/rss.xml",
     "site": "https://openai.com/news/", "category": "lab", "weight": 2.4},

    {"key": "google_ai", "name": "Google – The Keyword (AI)", "type": "rss",
     "url": "https://blog.google/technology/ai/rss/",
     "site": "https://blog.google/technology/ai/", "category": "lab", "weight": 2.0},

    {"key": "google_research", "name": "Google Research Blog", "type": "rss",
     "url": "https://research.google/blog/rss/",
     "site": "https://research.google/blog/", "category": "lab", "weight": 2.0},

    {"key": "msr", "name": "Microsoft Research", "type": "rss",
     "url": "https://www.microsoft.com/en-us/research/feed/",
     "site": "https://www.microsoft.com/en-us/research/", "category": "lab", "weight": 1.7},

    {"key": "apple_ml", "name": "Apple Machine Learning Research", "type": "rss",
     "url": "https://machinelearning.apple.com/rss.xml",
     "site": "https://machinelearning.apple.com/", "category": "lab", "weight": 1.6},

    {"key": "huggingface", "name": "Hugging Face Blog", "type": "rss",
     "url": "https://huggingface.co/blog/feed.xml",
     "site": "https://huggingface.co/blog", "category": "lab", "weight": 2.2},

    # 註：LangChain 的官方 RSS（blog.langchain.com/rss/）目前回傳 HTML 而非 XML，
    # 無法解析，暫時移除；之後若修好可再加回來。

    # ---------- 實務工作者 / 電子報（轉職 AI Engineer 最補的一區）----------
    {"key": "eugeneyan", "name": "Eugene Yan", "type": "rss",
     "url": "https://eugeneyan.com/rss/",
     "site": "https://eugeneyan.com/", "category": "practitioner", "weight": 2.8},

    {"key": "huyenchip", "name": "Chip Huyen", "type": "rss",
     "url": "https://huyenchip.com/feed.xml",
     "site": "https://huyenchip.com/", "category": "practitioner", "weight": 2.8},

    {"key": "lilianweng", "name": "Lil'Log (Lilian Weng)", "type": "rss",
     "url": "https://lilianweng.github.io/index.xml",
     "site": "https://lilianweng.github.io/", "category": "practitioner", "weight": 2.4},

    {"key": "simonwillison", "name": "Simon Willison's Weblog", "type": "rss",
     "url": "https://simonwillison.net/atom/everything/",
     "site": "https://simonwillison.net/", "category": "practitioner", "weight": 2.2},

    {"key": "dew", "name": "Data Engineering Weekly", "type": "rss",
     "url": "https://www.dataengineeringweekly.com/feed",
     "site": "https://www.dataengineeringweekly.com/", "category": "practitioner", "weight": 2.5},

    {"key": "seattledataguy", "name": "SeattleDataGuy", "type": "rss",
     "url": "https://seattledataguy.substack.com/feed",
     "site": "https://seattledataguy.substack.com/", "category": "practitioner", "weight": 2.0},

    {"key": "materializedview", "name": "Materialized View (Chris Riccomini)", "type": "rss",
     "url": "https://materializedview.io/feed",
     "site": "https://materializedview.io/", "category": "practitioner", "weight": 2.0},

    {"key": "ssp", "name": "Simon Späti – Data Engineering Design", "type": "rss",
     "url": "https://www.ssp.sh/index.xml",
     "site": "https://www.ssp.sh/", "category": "practitioner", "weight": 1.8},

    {"key": "maarten", "name": "Maarten Grootendorst (Visual Guides)", "type": "rss",
     "url": "https://newsletter.maartengrootendorst.com/feed",
     "site": "https://newsletter.maartengrootendorst.com/", "category": "practitioner", "weight": 2.0},

    {"key": "pragmatic", "name": "The Pragmatic Engineer", "type": "rss",
     "url": "https://newsletter.pragmaticengineer.com/feed",
     "site": "https://newsletter.pragmaticengineer.com/", "category": "practitioner", "weight": 1.8},

    {"key": "dagworks", "name": "DAGWorks / Hamilton", "type": "rss",
     "url": "https://blog.dagworks.io/feed",
     "site": "https://blog.dagworks.io/", "category": "practitioner", "weight": 1.5},

    # ---------- 研究 ----------
    {"key": "arxiv_lg", "name": "arXiv cs.LG (Machine Learning)", "type": "rss",
     "url": "https://arxiv.org/rss/cs.LG",
     "site": "https://arxiv.org/list/cs.LG/recent", "category": "research", "weight": 0.6},
]

CATEGORY_LABELS = {
    "core": "核心來源",
    "eng": "大廠工程部落格",
    "lab": "模型／平台官方",
    "practitioner": "實務工作者與電子報",
    "research": "研究論文",
}


def active_sources() -> list[dict]:
    return [s for s in SOURCES if s.get("type") == "rss"]


def manual_sources() -> list[dict]:
    return [s for s in SOURCES if s.get("type") == "manual"]
