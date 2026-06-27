"""
📦 海外仓资讯 — 价格 / 快递渠道 / 新闻
数据源: 物流行业网站爬虫 + RSS
"""

import feedparser
from utils import safe_request, cache_data


SOURCES = [
    ("https://www.supplychaindive.com/feeds/news/", "Supply Chain Dive"),
    ("https://www.logisticsmgmt.com/rss", "Logistics Management"),
    ("https://www.joc.com/rss", "JOC"),
]


def fetch_warehouse_news():
    """
    获取海外仓/物流行业最新资讯
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
            print(f"[海外仓] {source_name} 获取失败: {e}")

    # 过滤仓库/物流相关关键词
    keywords = ["warehouse", "fulfillment", "logistics", "shipping", "delivery",
                "freight", "supply chain", "海外仓", "仓储", "物流"]
    filtered = []
    for item in news:
        text = item["title"] + " " + item["summary"]
        if any(kw.lower() in text.lower() for kw in keywords):
            filtered.append(item)

    cache_data("warehouse_news.json", filtered)
    return filtered


def get_warehouse_data():
    """获取海外仓数据"""
    news = fetch_warehouse_news()
    return {"news": news}
