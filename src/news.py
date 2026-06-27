"""
📰 十大新闻 — 美国 / 中国 / 国际
数据源:
  - NewsAPI (需免费注册 Key)
  - 备用 RSS: BBC, Reuters, 新华网
"""

import json
import feedparser
from utils import safe_request, cache_data

# NewsAPI Key — 用户需注册
# 注册: https://newsapi.org/register
NEWSAPI_KEY = ""  # TODO: 用户填写
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


def fetch_newsapi(country, keyword=None, page_size=10):
    """
    从 NewsAPI 获取头条新闻
    country: 'us', 'cn' 等
    返回: list of {title, source, publishedAt, description, url}
    """
    if not NEWSAPI_KEY:
        return _fetch_rss_fallback(country)

    params = f"country={country}&pageSize={page_size}&apiKey={NEWSAPI_KEY}"
    if keyword:
        params += f"&q={keyword}"

    url = f"{NEWSAPI_URL}?{params}"
    data = safe_request(url)
    if not data:
        return _fetch_rss_fallback(country)

    try:
        result = json.loads(data)
        articles = result.get("articles", [])
        news = []
        for article in articles[:page_size]:
            news.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", ""),
                "published": article.get("publishedAt", "")[:10],
                "description": (article.get("description") or "")[:200],
                "url": article.get("url", ""),
            })
        return news
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[新闻] NewsAPI 解析错误: {e}")
        return _fetch_rss_fallback(country)


def _fetch_rss_fallback(country):
    """RSS 降级方案"""
    rss_feeds = {
        "us": [
            ("https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml", "BBC"),
            ("https://rss.nytimes.com/services/xml/rss/nyt/US.xml", "NYT"),
        ],
        "cn": [
            ("http://www.xinhuanet.com/english/rss/worldrss.xml", "Xinhua"),
            ("https://feedx.net/rss/chinadaily.xml", "China Daily"),
        ],
        "international": [
            ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
            ("https://www.reutersagency.com/feed/", "Reuters"),
        ],
    }

    feeds = rss_feeds.get(country, rss_feeds["international"])
    news = []
    for feed_url, source in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:8]:
                news.append({
                    "title": entry.get("title", ""),
                    "source": source,
                    "published": entry.get("published", "")[:10],
                    "description": (entry.get("summary") or "")[:200],
                    "url": entry.get("link", ""),
                })
        except Exception as e:
            print(f"[RSS] {source} 获取失败: {e}")
        if len(news) >= 10:
            break

    return news[:10]


def get_news_data():
    """
    获取新闻数据
    返回: {us: [], china: [], international: []}
    """
    return {
        "us": fetch_newsapi("us"),
        "china": fetch_newsapi("cn", keyword="China"),
        "international": fetch_newsapi(None, keyword="world") or _fetch_rss_fallback("international"),
    }
