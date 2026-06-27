"""
🛢️ 原油 + 汽油价格 — 当日值 + 近 1 年历史趋势
数据源:
  - 原油: Yahoo Finance (CL=F 历史区间)
  - 汽油: EIA API (免费注册获取 Key)
"""

import json
import urllib.parse
from datetime import datetime, timedelta
from utils import safe_request, cache_data, load_cache

# EIA API Key — 用户需自行注册
# 注册: https://www.eia.gov/opendata/register.php
EIA_API_KEY = ""  # TODO: 用户填写


def fetch_crude_oil_history():
    """
    获取 WTI 原油近 1 年历史价格
    使用 Yahoo Finance v8 chart API
    返回: list of {date, close}
    """
    url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"
    params = {
        "range": "1y",
        "interval": "1d",
        "includePrePost": "false",
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    data = safe_request(full_url, headers=headers)
    if not data:
        return load_cache("crude_oil_history.json", max_age_hours=48) or []

    try:
        result = json.loads(data)
        result = result.get("chart", {}).get("result", [])
        if not result:
            return load_cache("crude_oil_history.json", max_age_hours=48) or []

        result = result[0]
        timestamps = result.get("timestamp", [])
        quotes = result.get("indicators", {}).get("quote", [{}])[0]
        closes = quotes.get("close", [])

        history = []
        for i in range(len(timestamps)):
            if i < len(closes) and closes[i] is not None:
                history.append({
                    "date": datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d"),
                    "close": round(closes[i], 2),
                })

        cache_data("crude_oil_history.json", history)
        return history
    except Exception as e:
        print(f"[原油历史] 解析错误: {e}")
        return load_cache("crude_oil_history.json", max_age_hours=48) or []


def fetch_gas_prices():
    """
    获取美国各油号汽油价格（当日均价）
    使用 EIA API
    如果未配置 Key，返回模拟数据
    返回: dict of {regular, midgrade, premium, diesel}
    """
    if not EIA_API_KEY:
        print("[汽油] 未配置 EIA API Key，使用备用数据")
        return {
            "regular": 3.45,
            "midgrade": 3.85,
            "premium": 4.15,
            "diesel": 3.95,
            "unit": "USD/加仑",
            "source": "备用数据（请配置 EIA API Key）",
        }

    series_ids = {
        "regular": "PET.EMD_EPD2D_PTE_NUS_DPG.W",
        "midgrade": "PET.EMD_EPD2M_PTE_NUS_DPG.W",
        "premium": "PET.EMD_EPD2P_PTE_NUS_DPG.W",
        "diesel": "PET.EMD_EPD2D_PTD_NUS_DPG.W",
    }

    prices = {"unit": "USD/加仑"}
    for label, sid in series_ids.items():
        url = f"https://api.eia.gov/v2/seriesid/{sid}?api_key={EIA_API_KEY}"
        data = safe_request(url)
        if data:
            try:
                result = json.loads(data)
                series = result.get("response", {}).get("data", [])
                if series:
                    prices[label] = round(float(series[0]["value"]), 3)
                    continue
            except Exception:
                pass
        prices[label] = None

    # 如果有缺失，用最近缓存
    cached = load_cache("gas_prices_cache.json", max_age_hours=48)
    if cached:
        for label in ["regular", "midgrade", "premium", "diesel"]:
            if prices.get(label) is None and cached.get(label):
                prices[label] = cached[label]

    cache_data("gas_prices_cache.json", prices)
    return prices


def get_oil_gas_data():
    """
    综合获取原油+汽油数据
    返回: {crude: dict, gas: dict}
    """
    history = fetch_crude_oil_history()
    current_price = history[-1]["close"] if history else None
    previous_close = history[-2]["close"] if len(history) >= 2 else None

    change = None
    change_pct = None
    if current_price and previous_close:
        change = round(current_price - previous_close, 2)
        change_pct = round((change / previous_close) * 100, 2)

    crude = {
        "current_price": current_price,
        "previous_close": previous_close,
        "change": change,
        "change_pct": change_pct,
        "history": history,
        "unit": "USD/桶 (WTI)",
    }

    gas = fetch_gas_prices()

    return {"crude": crude, "gas": gas}
