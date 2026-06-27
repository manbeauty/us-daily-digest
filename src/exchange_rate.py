"""
美元/人民币汇率及主要货币汇率数据获取
数据来源: open.er-api.com (免费，无需 API Key)
"""

import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime


def fetch_exchange_rates():
    """
    获取美元兑主要货币汇率
    返回: dict 包含汇率数据，失败时返回 None
    """
    url = "https://open.er-api.com/v6/latest/USD"

    # 创建不验证 SSL 证书的 context（解决某些环境证书问题）
    ssl_context = ssl.create_default_context()

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

        if data.get("result") != "success":
            return None

        rates = data.get("rates", {})

        return {
            "USD_CNY": rates.get("CNY"),          # 美元兑人民币
            "USD_EUR": rates.get("EUR"),          # 美元兑欧元
            "USD_JPY": rates.get("JPY"),          # 美元兑日元
            "USD_GBP": rates.get("GBP"),          # 美元兑英镑
            "USD_CAD": rates.get("CAD"),          # 美元兑加元
            "USD_AUD": rates.get("AUD"),          # 美元兑澳元
            "USD_CHF": rates.get("CHF"),          # 美元兑瑞士法郎
            "update_time": data.get("time_update_us", datetime.now().isoformat()),
        }

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            ConnectionError, TimeoutError) as e:
        print(f"[汇率] 数据获取失败: {e}")
        return None


def format_exchange_rate_report(rates):
    """将汇率数据格式化为可读文本"""
    if not rates:
        return "⚠️ 汇率数据暂时无法获取"

    lines = [
        f"💱 美元/人民币 (USD/CNY): **{rates['USD_CNY']:.4f}**",
        f"💶 美元/欧元 (USD/EUR): {rates['USD_EUR']:.4f}",
        f"💴 美元/日元 (USD/JPY): {rates['USD_JPY']:.2f}",
        f"💷 美元/英镑 (USD/GBP): {rates['USD_GBP']:.4f}",
        f"💵 美元/加元 (USD/CAD): {rates['USD_CAD']:.4f}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    data = fetch_exchange_rates()
    if data:
        print("=== 汇率数据 ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
        print(format_exchange_rate_report(data))
    else:
        print("获取汇率数据失败")
