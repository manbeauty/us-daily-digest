"""
美国地道俚语和网络流行语采集
数据来源:
  - Urban Dictionary API (随机热门词条)
  - Reddit 热门帖子 (英语学习/俚语板块)
均无需 API Key
"""

import json
import urllib.request
import urllib.error
import ssl
import random
from datetime import datetime


# ============================================================
# 备用内置词库（当外部 API 不可用时的兜底数据）
# ============================================================
FALLBACK_SLANGS = [
    {
        "word": "GOAT",
        "meaning": "史上最佳 (Greatest Of All Time)",
        "example": "LeBron is the GOAT of basketball.",
        "source": "备用词库"
    },
    {
        "word": "No cap",
        "meaning": "不撒谎、说真的（字面 '没有帽子'，但 cap 俚语里是撒谎的意思）",
        "example": "No cap, that movie was amazing.",
        "source": "备用词库"
    },
    {
        "word": "Ghost",
        "meaning": "突然消失/失联（不回复消息、不接电话）",
        "example": "We went on three dates, and then he ghosted me.",
        "source": "备用词库"
    },
    {
        "word": "Slay",
        "meaning": "做得非常出色/惊艳（尤其指穿搭、表演）",
        "example": "You totally slayed that presentation!",
        "source": "备用词库"
    },
    {
        "word": "Bet",
        "meaning": "没问题/行/确定了（表示同意或确认）",
        "example": 'A: "Wanna grab pizza?" B: "Bet."',
        "source": "备用词库"
    },
    {
        "word": "Bussin'",
        "meaning": "超级好吃/非常棒",
        "example": "This pasta is bussin' fr!",
        "source": "备用词库"
    },
    {
        "word": "Sus",
        "meaning": "可疑的/靠不住的（suspicious 的缩写）",
        "example": "That guy's acting really sus.",
        "source": "备用词库"
    },
    {
        "word": "Flex",
        "meaning": "炫耀/显摆",
        "example": "He's just flexing his new car.",
        "source": "备用词库"
    },
    {
        "word": "Stan",
        "meaning": "狂热粉丝/疯狂支持（源于 Eminem 的歌）",
        "example": "I stan that singer so hard.",
        "source": "备用词库"
    },
    {
        "word": "Extra",
        "meaning": "夸张/过火/做作",
        "example": "She's so extra with all those filters.",
        "source": "备用词库"
    },
    {
        "word": "Lowkey",
        "meaning": "低调地/有点（表示低调承认某件事）",
        "example": "I lowkey want to stay home today.",
        "source": "备用词库"
    },
    {
        "word": "Highkey",
        "meaning": "坦率地/大大方方地（与 lowkey 相对）",
        "example": "I highkey love this song.",
        "source": "备用词库"
    },
    {
        "word": "Yeet",
        "meaning": "用力扔/抛弃（也表示兴奋时的喊叫）",
        "example": "He yeeted the ball across the field.",
        "source": "备用词库"
    },
    {
        "word": "FOMO",
        "meaning": "错失恐惧症 (Fear Of Missing Out)",
        "example": "I have major FOMO seeing everyone at the party.",
        "source": "备用词库"
    },
    {
        "word": "Cringe",
        "meaning": "尴尬/令人不适/尬到不行",
        "example": "That TikTok dance was so cringe.",
        "source": "备用词库"
    },
]


def fetch_urban_dictionary(count=5):
    """
    从 Urban Dictionary 获取随机词条
    返回: list of dict，每个包含 word, meaning, example
    """
    url = "https://api.urbandictionary.com/v0/random"
    ssl_context = ssl.create_default_context()
    results = []

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "USDailyDigest/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        entries = data.get("list", [])
        # 过滤不合适的词条（包含过多 NSFW 内容）
        filtered = []
        bad_keywords = [
            "porn", "sex", "nsfw", "fuck", "shit", "bitch", "asshole",
            "dick", "pussy", "cock", "whore", "slut"
        ]

        for entry in entries:
            word = entry.get("word", "")
            definition = entry.get("definition", "")
            example = entry.get("example", "")

            # 简单过滤
            word_lower = word.lower()
            def_lower = definition.lower()
            if any(kw in word_lower or kw in def_lower for kw in bad_keywords):
                continue

            # 清理 definition 和 example 中的特殊字符
            definition = definition.replace("\r\n", " ").replace("\n", " ").strip()
            example = example.replace("\r\n", " ").replace("\n", " ").strip()

            filtered.append({
                "word": word[:50],
                "meaning": definition[:300],
                "example": example[:300] if example else "（无例句）",
                "source": "Urban Dictionary",
            })

        # 打乱后取前 count 个
        random.shuffle(filtered)
        results = filtered[:count]

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            ConnectionError, TimeoutError) as e:
        print(f"[俚语] Urban Dictionary 获取失败: {e}")

    return results


def fetch_reddit_slang(count=5):
    """
    从 Reddit 获取俚语相关帖子
    来源: r/slang, r/EnglishLearning 等
    返回: list of dict
    """
    subreddits = ["slang", "EnglishLearning", "words", "DoesAnybodyElse"]
    ssl_context = ssl.create_default_context()
    results = []

    # 随机选一个 subreddit
    subreddit = random.choice(subreddits)
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "USDailyDigest/1.0 (by /u/daily_digest_bot)"
                ),
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        children = data.get("data", {}).get("children", [])

        for child in children:
            post = child.get("data", {})
            title = post.get("title", "")
            selftext = post.get("selftext", "")

            # 只处理文本帖且标题看起来像是讨论词汇/俚语的
            keywords = [
                "what does", "meaning", "slang", "phrase", "word",
                "say", "term", "called", "俚语"
            ]
            title_lower = title.lower()
            if not any(kw in title_lower for kw in keywords):
                continue

            # 提取可能是关键词的词汇（取标题中首次出现的未知词）
            text = (title + " " + selftext)[:500]
            text = text.replace("\r\n", " ").replace("\n", " ").strip()

            results.append({
                "word": title[:80],
                "meaning": text[:300],
                "example": "（来自 Reddit 讨论帖）",
                "source": f"Reddit r/{subreddit}",
            })

            if len(results) >= count:
                break

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            ConnectionError, TimeoutError) as e:
        print(f"[俚语] Reddit 获取失败: {e}")

    return results


def fetch_all_slang(total_count=10):
    """
    综合获取俚语数据：Urban Dictionary + Reddit + 备用词库
    返回: list of dict
    """
    urban_count = total_count // 2
    reddit_count = total_count - urban_count

    # 并行获取（顺序请求但快速）
    urban_slangs = fetch_urban_dictionary(urban_count)
    reddit_slangs = fetch_reddit_slang(reddit_count)

    all_slangs = urban_slangs + reddit_slangs
    random.shuffle(all_slangs)

    # 如果获取的数量不足，用备用词库补齐
    if len(all_slangs) < total_count:
        needed = total_count - len(all_slangs)
        # 从不重复的备用词中选取
        used_words = {s["word"].lower() for s in all_slangs}
        available = [
            s for s in FALLBACK_SLANGS
            if s["word"].lower() not in used_words
        ]
        random.shuffle(available)
        all_slangs.extend(available[:needed])

    # 只返回需要的数量
    return all_slangs[:total_count]


def format_slang_report(slangs):
    """将俚语数据格式化为可读文本"""
    if not slangs:
        return "⚠️ 俚语数据暂时无法获取"

    lines = []
    for i, s in enumerate(slangs, 1):
        lines.append(f"{i}. **{s['word']}**")
        lines.append(f"   📖 {s['meaning']}")
        lines.append(f"   💬 {s['example']}")
        lines.append(f"   📌 {s['source']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print("=== 俚语数据 ===")
    slangs = fetch_all_slang(10)
    for s in slangs:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        print("---")
    print()
    print(format_slang_report(slangs))
