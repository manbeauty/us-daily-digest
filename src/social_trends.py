"""
📱 社交热点 — Google Trends + Reddit 热门 + 网络用语
数据源:
  - Google Trends: pytrends 库
  - Reddit: reddit.com/.json (免 Key)
"""

import json
from utils import safe_request, cache_data

# 备用网络用语库
TRENDING_WORDS = [
    {"word": "Rizz", "meaning": "魅力/吸引力（charisma 的缩写）", "example": "He's got mad rizz."},
    {"word": "Slay", "meaning": "做得非常出色", "example": "She slayed that performance."},
    {"word": "No cap", "meaning": "不撒谎，说真的", "example": "No cap, this is the best pizza ever."},
    {"word": "Bet", "meaning": "没问题/行", "example": "Bet, I'll see you there."},
    {"word": "Sus", "meaning": "可疑的（suspicious）", "example": "That's kinda sus."},
    {"word": "Ghost", "meaning": "突然失联", "example": "He ghosted me after 3 dates."},
    {"word": "Flex", "meaning": "炫耀", "example": "Just flexing my new setup."},
    {"word": "Stan", "meaning": "狂热粉丝", "example": "I stan that artist."},
    {"word": "GOAT", "meaning": "史上最佳", "example": "Greatest Of All Time."},
    {"word": "FOMO", "meaning": "错失恐惧症", "example": "I have major FOMO right now."},
]


def fetch_reddit_hot():
    """
    获取 Reddit 热门帖子标题
    返回: list of {title, subreddit, score, url}
    """
    url = "https://www.reddit.com/hot.json?limit=25"
    data = safe_request(url, headers={
        "User-Agent": "USDailyDigest/2.0 (by /u/daily_digest_bot)"
    })
    if not data:
        return []

    try:
        result = json.loads(data)
        children = result.get("data", {}).get("children", [])
        posts = []
        for child in children[:20]:
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", "")[:120],
                "subreddit": post.get("subreddit", ""),
                "score": post.get("score", 0),
                "url": post.get("url", ""),
            })
        return posts
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Reddit] 解析错误: {e}")
        return []


def fetch_google_trends():
    """
    获取 Google Trends 今日热搜
    使用 pytrends 库
    返回: list of {keyword, 热度}
    """
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=300)
        trending = pytrends.trending_searches(pn="united_states")
        if trending is not None and not trending.empty:
            keywords = trending[0].head(15).tolist()
            return [{"keyword": kw, "source": "Google Trends"} for kw in keywords]
    except Exception as e:
        print(f"[Google Trends] 获取失败: {e}")

    return []


def get_social_data():
    """
    综合获取社交热点数据
    返回: {trends: [], reddit: [], slang: []}
    """
    trends = fetch_google_trends()
    reddit = fetch_reddit_hot()
    return {
        "trends": trends,
        "reddit": reddit,
        "slang": TRENDING_WORDS,
    }
