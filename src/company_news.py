"""
🏢 企业/品牌动态
跟踪: 万邑通、乐歌、赛维时代、迅邮、美通、鑫亚、Worldwide Express
园林品牌: Litheli、Greenworks、Ego、Powersmart
"""

import feedparser
from utils import safe_request, cache_data


# 搜索关键词列表
COMPANIES = [
    "万邑通", "乐歌", "赛维时代", "迅邮物流", "美通物流", "鑫亚物流",
    "Worldwide Express", "Worldwide Express logistics",
    "Litheli", "Greenworks", "EGO Power", "Powersmart",
]

# 新闻源
NEWS_FEEDS = [
    ("https://news.google.com/rss/search?q={q}&hl=en-US&gl=US", "Google News"),
    ("https://www.prnewswire.com/rss/search.rss?keyword={q}", "PRNewswire"),
]


def fetch_company_news():
    """
    获取所有关注企业的动态
    返回: list of {title, source, date, summary, url, company}
    """
    all_news = []

    for company in COMPANIES:
        for feed_tpl, source_name in NEWS_FEEDS:
            feed_url = feed_tpl.format(q=company.replace(" ", "+"))
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    all_news.append({
                        "title": entry.get("title", ""),
                        "source": source_name,
                        "date": entry.get("published", "")[:10],
                        "summary": (entry.get("summary") or "")[:200],
                        "url": entry.get("link", ""),
                        "company": company,
                    })
            except Exception as e:
                print(f"[企业动态] {company}@{source_name}: {e}")

    # 去重
    seen = set()
    unique = []
    for item in all_news:
        key = item["title"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    cache_data("company_news.json", unique)
    return unique


def get_company_data():
    return {"news": fetch_company_news()}
