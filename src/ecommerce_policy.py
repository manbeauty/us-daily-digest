"""
🏪 电商平台政策变化 — Amazon / Walmart / TikTok Shop / eBay
数据源: 官方博客 RSS + 新闻稿
"""

import feedparser
from utils import safe_request, cache_data


SOURCES = [
    ("https://sellercentral.amazon.com/forums/announcements", "Amazon Seller Central"),
    ("https://www.walmart.com/marketplace/rss/news", "Walmart Marketplace"),
    ("https://newsroom.tiktok.com/en-us/feed.xml", "TikTok Newsroom"),
    ("https://community.ebay.com/t5/Announcements/bd-p/Announcements", "eBay"),
    ("https://www.shopify.com/blog/feed", "Shopify Blog"),
]


def fetch_policy_news():
    """
    获取电商政策最新变化
    返回: list of {title, source, date, summary, url}
    """
    news = []
    for feed_url, source_name in SOURCES:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:4]:
                news.append({
                    "title": entry.get("title", ""),
                    "source": source_name,
                    "date": entry.get("published", "")[:10],
                    "summary": (entry.get("summary") or "")[:200],
                    "url": entry.get("link", ""),
                })
        except Exception as e:
            print(f"[电商政策] {source_name} 获取失败: {e}")

    cache_data("ecommerce_policy.json", news)
    return news


def get_ecommerce_policy_data():
    """获取电商政策数据"""
    return {"news": fetch_policy_news()}
