"""
美国各州首府一周天气预报获取
数据来源: National Weather Service API (api.weather.gov)
完全免费，无需 API Key
"""

import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime
import os
import sys


def load_states():
    """加载州数据"""
    states_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "states.json")
    try:
        with open(states_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("states", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[天气] 加载州数据失败: {e}")
        return []


def fetch_forecast_for_city(city_name, state_abbr, latitude, longitude):
    """
    获取单个城市的天气预报
    使用 NWS API:
      1. /points/{lat},{lon} 获取预报端点
      2. 访问 forecast URL 获取 7 天预报
    返回: dict 或 None
    """
    ssl_context = ssl.create_default_context()
    headers = {
        "User-Agent": "(USDailyDigest, contact@usdailydigest.dev)",
        "Accept": "application/json",
    }

    try:
        # Step 1: 获取网格信息
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        req = urllib.request.Request(points_url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
            points_data = json.loads(response.read().decode("utf-8"))

        forecast_url = points_data.get("properties", {}).get("forecast")
        if not forecast_url:
            return None

        # Step 2: 获取天气预报
        req2 = urllib.request.Request(forecast_url, headers=headers)
        with urllib.request.urlopen(req2, context=ssl_context, timeout=15) as response:
            forecast_data = json.loads(response.read().decode("utf-8"))

        periods = forecast_data.get("properties", {}).get("periods", [])
        if not periods:
            return None

        # 提取每天白天的预报（NWS 返回的是 day/night 交替）
        daily = []
        for period in periods:
            if period.get("isDaytime", False):  # 只取白天数据
                daily.append({
                    "date": period.get("name", ""),  # e.g. "Today", "Monday"
                    "temperature": period.get("temperature"),
                    "temp_unit": period.get("temperatureUnit", "F"),
                    "wind_speed": period.get("windSpeed", ""),
                    "wind_direction": period.get("windDirection", ""),
                    "short_forecast": period.get("shortForecast", ""),
                    "detailed_forecast": period.get("detailedForecast", ""),
                    "icon_url": period.get("icon", ""),
                })

        return {
            "city": city_name,
            "state": state_abbr,
            "daily": daily[:7],  # 最多 7 天
        }

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            ConnectionError, TimeoutError) as e:
        print(f"[天气] {city_name}, {state_abbr} 数据获取失败: {e}")
        return None


def fetch_all_weather():
    """
    获取所有州的天气预报
    返回: list of dict
    """
    states = load_states()
    results = []

    for i, state in enumerate(states):
        print(f"[天气] 正在获取 {state['name_cn']} ({state['capital']}) 的天气... "
              f"({i+1}/{len(states)})")

        forecast = fetch_forecast_for_city(
            state["capital"],
            state["abbr"],
            state["latitude"],
            state["longitude"],
        )

        if forecast:
            forecast["state_name_cn"] = state["name_cn"]
            forecast["rank"] = state["rank"]
            results.append(forecast)

        # NWS API 有限制，短时间隔
        import time
        time.sleep(0.5)

    # 按人口排名排序
    results.sort(key=lambda x: x.get("rank", 999))

    return results


def format_weather_report(weather_data):
    """将天气数据格式化为可读文本"""
    if not weather_data:
        return "⚠️ 天气数据暂时无法获取"

    lines = []
    for w in weather_data:
        lines.append(f"\n🌤️ **{w['state_name_cn']} ({w['city']}, {w['state']})**")
        for day in w.get("daily", []):
            temp = day["temperature"]
            unit = day["temp_unit"]
            forecast = day["short_forecast"]
            wind = f"{day['wind_speed']} {day['wind_direction']}"
            lines.append(
                f"   {day['date']}: {temp}°{unit} | {forecast} | 💨 {wind}"
            )

    return "\n".join(lines)


def get_weather_icon(short_forecast):
    """根据天气预报文本返回合适的 emoji"""
    forecast_lower = short_forecast.lower()

    if any(kw in forecast_lower for kw in ["sunny", "clear"]):
        return "☀️"
    elif any(kw in forecast_lower for kw in ["partly cloudy", "mostly cloudy"]):
        return "⛅"
    elif any(kw in forecast_lower for kw in ["cloudy", "overcast"]):
        return "☁️"
    elif any(kw in forecast_lower for kw in ["rain", "showers", "drizzle"]):
        return "🌧️"
    elif any(kw in forecast_lower for kw in ["thunderstorm", "t-storm"]):
        return "⛈️"
    elif any(kw in forecast_lower for kw in ["snow", "blizzard"]):
        return "❄️"
    elif any(kw in forecast_lower for kw in ["fog", "mist", "haze"]):
        return "🌫️"
    elif any(kw in forecast_lower for kw in ["wind"]):
        return "💨"
    else:
        return "🌤️"


if __name__ == "__main__":
    print("=== 天气预报 ===")
    weather = fetch_all_weather()
    if weather:
        print(f"成功获取 {len(weather)} 个城市的天气")
        print(format_weather_report(weather))
    else:
        print("获取天气数据失败")
