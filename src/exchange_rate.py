"""
💱 美元/人民币汇率 — 当日值 + 近 1 年历史趋势
数据源:
  - 当日: open.er-api.com (免 Key)
  - 历史: frankfurter.app (免 Key, 支持日期区间查询)
"""

import json
from datetime import datetime, timedelta
from utils import safe_request, cache_data, load_cache


def fetch_daily_rate():
    """
    获取当日美元兑主要货币汇率
    返回: dict 或 None
    """
    url = "https://open.er-api.com/v6/latest/USD"
    data = safe_request(url)
    if not data:
        return None

    try:
        result = json.loads(data)
        if result.get("result") != "success":
            return None
        rates = result.get("rates", {})
        return {
            "USD_CNY": rates.get("CNY"),
            "USD_EUR": rates.get("EUR"),
            "USD_JPY": rates.get("JPY"),
            "USD_GBP": rates.get("GBP"),
            "USD_CAD": rates.get("CAD"),
            "USD_AUD": rates.get("AUD"),
            "USD_CHF": rates.get("CHF"),
        }
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[汇率] 解析错误: {e}")
        return None


def fetch_history_1y():
    """
    获取 USD/CNY 近 1 年历史汇率
    使用 frankfurter.app API
    返回: list of {date, rate}
    """
    # 计算日期范围（过去 365 天）
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    date_from = start_date.strftime("%Y-%m-%d")
    date_to = end_date.strftime("%Y-%m-%d")

    url = f"https://api.frankfurter.app/{date_from}..{date_to}?from=USD&to=CNY"
    data = safe_request(url)
    if not data:
        # 降级：从缓存读取
        cached = load_cache("exchange_rate_history.json", max_age_hours=48)
        return cached or []

    try:
        result = json.loads(data)
        rates = result.get("rates", {})
        history = []
        for date_str in sorted(rates.keys()):
            if "CNY" in rates[date_str]:
                history.append({
                    "date": date_str,
                    "rate": round(rates[date_str]["CNY"], 4)
                })
        # 缓存
        cache_data("exchange_rate_history.json", history)
        return history
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[汇率历史] 解析错误: {e}")
        cached = load_cache("exchange_rate_history.json", max_age_hours=48)
        return cached or []


def get_exchange_rate_data():
    """
    综合获取汇率数据
    返回: {current: dict, history: list}
    """
    today = fetch_daily_rate()
    history = fetch_history_1y()

    # 如果有当日数据，追加到历史
    if today and "USD_CNY" in today:
        today_record = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "rate": today["USD_CNY"]
        }
        # 检查最后一条是否已为今天
        if history and history[-1]["date"] != today_record["date"]:
            history.append(today_record)

    return {
        "current": today,
        "history": history[-365:],  # 最多 365 天
    }
