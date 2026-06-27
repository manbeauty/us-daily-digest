"""
美国原油 (WTI) 价格数据获取
数据来源: Yahoo Finance 公开 API (免费，无需 API Key)
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
from datetime import datetime


def fetch_oil_price():
    """
    获取 WTI 原油期货价格
    使用 Yahoo Finance 的公开接口
    返回: dict 包含油价数据，失败时返回 None
    """
    # Yahoo Finance 获取 CL=F (WTI Crude Oil) 的报价
    # 使用 yfinance 的公开查询接口
    url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"

    ssl_context = ssl.create_default_context()

    params = {
        "range": "5d",       # 过去5个交易日
        "interval": "1d",
        "includePrePost": "false",
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    try:
        req = urllib.request.Request(
            full_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        result = data.get("chart", {}).get("result", [])
        if not result:
            return None

        result = result[0]
        meta = result.get("meta", {})
        indicators = result.get("indicators", {})
        quotes = indicators.get("quote", [{}])[0]
        timestamps = result.get("timestamp", [])

        # 当前/最新价格
        current_price = meta.get("regularMarketPrice")
        previous_close = meta.get("previousClose")
        currency = meta.get("currency", "USD")
        market_time = meta.get("regularMarketTime")

        # 获取最近几天的收盘价
        closes = quotes.get("close", [])
        close_prices = [c for c in closes if c is not None]

        # 构造历史价格列表
        history = []
        for i in range(len(timestamps)):
            if i < len(closes) and closes[i] is not None:
                history.append({
                    "date": datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d"),
                    "close": round(closes[i], 2),
                })

        if current_price is None and close_prices:
            current_price = close_prices[-1]

        change = None
        change_pct = None
        if current_price is not None and previous_close is not None:
            change = round(current_price - previous_close, 2)
            change_pct = round((change / previous_close) * 100, 2)

        return {
            "current_price": round(current_price, 2) if current_price else None,
            "previous_close": round(previous_close, 2) if previous_close else None,
            "change": change,
            "change_pct": change_pct,
            "currency": currency,
            "history": history[-7:] if len(history) > 7 else history,  # 最近7天
            "unit": "USD/桶 (WTI原油期货)",
            "update_time": datetime.utcfromtimestamp(market_time).strftime(
                "%Y-%m-%d %H:%M UTC"
            ) if market_time else datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            ConnectionError, TimeoutError) as e:
        print(f"[油价] 数据获取失败: {e}")
        return None


def format_oil_price_report(oil_data):
    """将油价数据格式化为可读文本"""
    if not oil_data:
        return "⚠️ 油价数据暂时无法获取"

    change_icon = "📈" if oil_data.get("change", 0) >= 0 else "📉"
    change_str = (
        f"+{oil_data['change']}" if oil_data.get("change", 0) >= 0
        else f"{oil_data['change']}"
    )
    change_pct_str = (
        f"+{oil_data['change_pct']}%" if oil_data.get("change_pct", 0) >= 0
        else f"{oil_data['change_pct']}%"
    )

    lines = [
        f"🛢️ WTI原油期货: **${oil_data['current_price']}** {oil_data['unit']}",
        f"   {change_icon} 较前日: {change_str} ({change_pct_str})",
        f"   📊 昨收: ${oil_data['previous_close']}",
    ]

    if oil_data.get("history"):
        lines.append("   📅 近7日收盘价:")
        for h in oil_data["history"]:
            lines.append(f"      {h['date']}: ${h['close']}")

    return "\n".join(lines)


if __name__ == "__main__":
    data = fetch_oil_price()
    if data:
        print("=== 油价数据 ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
        print(format_oil_price_report(data))
    else:
        print("获取油价数据失败")
