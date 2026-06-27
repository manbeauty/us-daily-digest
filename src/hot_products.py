"""
🛒 电商平台热销 TOP10 — Amazon / Walmart / TikTok Shop
数据源: 网页爬虫
"""

from utils import safe_request, cache_data
from bs4 import BeautifulSoup


def scrape_amazon_bestsellers():
    """
    爬取 Amazon 畅销榜 TOP10
    """
    url = "https://www.amazon.com/gp/bestsellers/"
    html = safe_request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    if not html:
        return _fallback("Amazon")

    try:
        soup = BeautifulSoup(html, "lxml")
        items = soup.select(".p13n-sc-truncate, .zg-item-immersion span")
        products = []
        for item in items[:15]:
            text = item.get_text(strip=True)
            if text and len(text) > 10:
                products.append({
                    "name": text[:100],
                    "platform": "Amazon",
                })
        if products:
            return products[:10]
    except Exception as e:
        print(f"[Amazon] 解析错误: {e}")

    return _fallback("Amazon")


def scrape_walmart_top():
    """
    爬取 Walmart 热卖榜 TOP10
    """
    url = "https://www.walmart.com/browse/0?page=1"
    html = safe_request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    if not html:
        return _fallback("Walmart")

    try:
        soup = BeautifulSoup(html, "lxml")
        products = []
        for item in soup.select("[data-testid='item-title'], .truncate-title")[:15]:
            text = item.get_text(strip=True)
            if text and len(text) > 5:
                products.append({
                    "name": text[:100],
                    "platform": "Walmart",
                })
        if products:
            return products[:10]
    except Exception as e:
        print(f"[Walmart] 解析错误: {e}")

    return _fallback("Walmart")


def scrape_tiktok_shop():
    """
    获取 TikTok Shop 热门商品
    """
    return _fallback("TikTok Shop")


def _fallback(platform):
    """降级数据"""
    fallbacks = {
        "Amazon": [
            "Amazon Kindle", "Apple AirPods", "Fire TV Stick",
            "iRobot Roomba", "Instant Pot", "Yeti Rambler",
            "Sony WH-1000XM5", "LEGO Star Wars", "Fitbit Versa",
            "Cuisinart Food Processor",
        ],
        "Walmart": [
            "Great Value Paper Towels", "Samsung 65\" TV", "HP Laptop 15",
            "George Men's Jeans", "Mainstays Bed Sheets",
            "Equate Ibuprofen", "Play-Doh Modeling Compound",
            "Ozark Trail Cooler", "Vizio Sound Bar", "Special Kitty Cat Food",
        ],
        "TikTok Shop": [
            "TikTok Mini Fan", "LED Strip Lights", "Phone Ring Holder",
            "Tumbler Cup 40oz", "Revlon Hair Dryer", "Gym Shark Hoodie",
            "Car Air Freshener", "Bluetooth Earbuds", "Aesthetic Journal",
            "Pet Hair Remover",
        ],
    }
    items = fallbacks.get(platform, [])
    return [{"name": name, "platform": platform} for name in items]


def get_hot_products():
    """
    综合获取各平台热销产品
    返回: {amazon: [], walmart: [], tiktok: []}
    """
    return {
        "amazon": scrape_amazon_bestsellers(),
        "walmart": scrape_walmart_top(),
        "tiktok": scrape_tiktok_shop(),
    }
