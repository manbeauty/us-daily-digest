"""
🛃 美国关税政策变化
数据源: USTR / CBP / 贸易新闻
"""

import feedparser
from utils import safe_request, cache_data


SOURCES = [
    ("https://ustr.gov/feed", "USTR"),
    ("https://www.cbp.gov/newsroom/rss", "CBP"),
    ("https://www.trade.gov/rss/news", "International Trade"),
    ("https://www.wto.org/english/news_e/news_e.rss", "WTO"),
]


def fetch_tariff_news():
    """
    获取关税政策最新变化
    返回: list of {title, source, date, summary, url}
    """
    news = []
    for feed_url, source_name in SOURCES:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                news.append({
                    "title": entry.get("title", ""),
                    "source": source_name,
                    "date": entry.get("published", "")[:10],
                    "summary": (entry.get("summary") or "")[:200],
                    "url": entry.get("link", ""),
                })
        except Exception as e:
            print(f"[关税] {source_name} 获取失败: {e}")

    # 过滤关税相关
    keywords = ["tariff", "trade", "duty", "import tax", "section 301", "section 232",
                "关税", "贸易", "301条款"]
    filtered = []
    for item in news:
        text = item["title"] + " " + item["summary"]
        if any(kw.lower() in text.lower() for kw in keywords):
            filtered.append(item)

    cache_data("tariff_news.json", filtered)
    return filtered


def get_tariff_data():
    return {"news": fetch_tariff_news()}
