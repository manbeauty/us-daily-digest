"""
🌡️ 美国 50 州温度采集（用于地图热力图）
数据源: NWS API (免 Key)
"""

import json
import os
import time
from utils import safe_request, cache_data, load_cache


def load_states():
    """加载 50 州数据"""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "states.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("states", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[温度] 加载州数据失败: {e}")
        return []


def fetch_state_temperature(state):
    """
    获取单个州首府当前温度
    返回: dict {abbr, state, capital, temperature_f, temperature_c} 或 None
    """
    url = (
        f"https://api.weather.gov/points/{state['latitude']},{state['longitude']}"
    )
    headers = {
        "User-Agent": "(USDailyDigest, contact@usdailydigest.dev)",
        "Accept": "application/json",
    }

    data = safe_request(url, headers=headers)
    if not data:
        return None

    try:
        result = json.loads(data)
        forecast_url = result.get("properties", {}).get("forecastHourly")
        if not forecast_url:
            return None

        hourly_data = safe_request(forecast_url, headers=headers)
        if not hourly_data:
            return None

        hourly = json.loads(hourly_data)
        periods = hourly.get("properties", {}).get("periods", [])
        if not periods:
            return None

        # 取当前小时（第一条）的温度
        temp_f = periods[0].get("temperature")
        if temp_f is None:
            return None

        temp_c = round((temp_f - 32) * 5 / 9, 1)

        return {
            "abbr": state["abbr"],
            "state": state["name"],
            "capital": state["capital"],
            "temperature_f": temp_f,
            "temperature_c": temp_c,
        }
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        print(f"[温度] {state['abbr']} 解析错误: {e}")
        return None


def fetch_all_temperatures():
    """
    获取所有 50 州的温度
    返回: list of dict
    """
    states = load_states()
    results = []

    for i, state in enumerate(states):
        print(f"[温度] {state['abbr']} ({i+1}/{len(states)})...")
        temp = fetch_state_temperature(state)
        if temp:
            results.append(temp)
        time.sleep(0.3)  # NWS API 限流

    # 缓存
    cache_data("temperatures.json", results)
    return results
