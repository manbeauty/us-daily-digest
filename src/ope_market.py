"""
🌿 OPE 园林产品市场资讯
数据源: 行业网站 RSS + 新闻爬虫
"""

import feedparser
from utils import safe_request, cache_data


RSS_FEEDS = [
    ("https://www.greenindustrypros.com/rss", "Green Industry Pros"),
    ("https://www.powerequipment.com/rss/", "Power Equipment"),
]

NEWS_SOURCES = [
    ("https://www.prnewswire.com/rss/lawn-garden.rss", "PRNewswire Lawn & Garden"),
]


def fetch_ope_news():
    """
    获取 OPE 园林市场最新资讯
    返回: list of {title, source, date, summary, url}
    """
    news = []

    # 从 RSS 获取
    for feed_url, source_name in RSS_FEEDS + NEWS_SOURCES:
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
            print(f"[OPE] {source_name} 获取失败: {e}")

    cache_data("ope_news.json", news)
    return news


def get_ope_data():
    """获取 OPE 市场数据"""
    news = fetch_ope_news()
    return {"news": news}
