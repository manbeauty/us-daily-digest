"""
🇺🇸 美国每日资讯日报 - 主入口
每天 9:00 (北京时间) 自动运行，生成 HTML 日报并部署到 GitHub Pages

运行方式:
    python src/main.py

输出:
    output/index.html  — 可直接在浏览器打开查看
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta

# 确保 src 目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exchange_rate import fetch_exchange_rates
from oil_price import fetch_oil_price
from slang import fetch_all_slang
from weather import fetch_all_weather, get_weather_icon


def load_template():
    """加载 HTML 模板"""
    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "template.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def render_oil_history(oil_data):
    """渲染油价历史趋势 HTML"""
    if not oil_data or not oil_data.get("history"):
        return ""

    history = oil_data["history"]
    rows = "".join(
        f"<tr><td>{h['date']}</td><td>${h['close']}</td></tr>"
        for h in history
    )
    return f"""
    <div class="oil-history">
        <h4>📅 近 {len(history)} 日收盘价走势</h4>
        <table>
            {rows}
        </table>
    </div>
    """


def render_slang_items(slangs):
    """渲染俚语列表 HTML"""
    if not slangs:
        return "<p>⚠️ 俚语数据暂时无法获取</p>"

    items = ""
    for s in slangs:
        items += f"""
        <li class="slang-item">
            <div class="slang-word">{s['word']}</div>
            <div class="slang-meaning">{s['meaning']}</div>
            <div class="slang-example">{s['example']}</div>
            <div class="slang-source">📌 {s['source']}</div>
        </li>
        """
    return items


def render_weather(weather_data):
    """渲染天气预报 HTML"""
    if not weather_data:
        return "<p>⚠️ 天气数据暂时无法获取</p>"

    html = ""
    for w in weather_data:
        state_cn = w.get("state_name_cn", "")
        city = w.get("city", "")
        state = w.get("state", "")

        days_html = ""
        for day in w.get("daily", []):
            temp = day["temperature"]
            unit = day["temp_unit"]
            forecast = day["short_forecast"]
            icon = get_weather_icon(forecast)

            days_html += f"""
            <div class="weather-day">
                <div class="day-name">{day['date']}</div>
                <div class="day-icon">{icon}</div>
                <div class="day-temp">{temp}°{unit}</div>
                <div class="day-forecast">{forecast}</div>
            </div>
            """

        html += f"""
        <div class="weather-state">
            <div class="weather-state-title">📌 {state_cn} — {city} ({state})</div>
            <div class="weather-grid">
                {days_html}
            </div>
        </div>
        """

    return html


def safe_val(value, fmt=".4f"):
    """安全格式化数值，处理 None"""
    if value is None:
        return "—"
    try:
        return format(float(value), fmt)
    except (ValueError, TypeError):
        return str(value)


def main():
    print("=" * 50)
    print("🇺🇸 美国每日资讯日报生成器")
    print("=" * 50)

    # 获取北京时间
    beijing_tz = timezone(timedelta(hours=8))
    now_beijing = datetime.now(beijing_tz)
    update_date = now_beijing.strftime("%Y年%m月%d日 %A")
    data_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    print(f"\n📅 当前时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print()

    # === 1. 获取汇率数据 ===
    print("📡 正在获取汇率数据...")
    rates = fetch_exchange_rates()
    if rates:
        print(f"   ✅ USD/CNY = {rates.get('USD_CNY', 'N/A')}")
    else:
        print("   ⚠️ 获取失败，使用占位符")

    # === 2. 获取油价数据 ===
    print("📡 正在获取油价数据...")
    oil = fetch_oil_price()
    if oil:
        print(f"   ✅ WTI原油 = ${oil.get('current_price', 'N/A')}")
    else:
        print("   ⚠️ 获取失败，使用占位符")

    # === 3. 获取俚语数据 ===
    print("📡 正在获取俚语数据...")
    slangs = fetch_all_slang(10)
    if slangs:
        print(f"   ✅ 获取 {len(slangs)} 条俚语")
    else:
        print("   ⚠️ 获取失败，使用备用词库")

    # === 4. 获取天气数据 ===
    print("📡 正在获取天气数据...")
    weather = fetch_all_weather()
    if weather:
        print(f"   ✅ 获取 {len(weather)} 个城市天气")
    else:
        print("   ⚠️ 获取失败")

    print()
    print("=" * 50)
    print("📝 正在生成 HTML 页面...")

    # === 渲染 HTML ===
    template = load_template()

    # 汇率
    usd_cny = safe_val(rates.get("USD_CNY"), ".4f") if rates else "—"
    usd_eur = safe_val(rates.get("USD_EUR"), ".4f") if rates else "—"
    usd_jpy = safe_val(rates.get("USD_JPY"), ".2f") if rates else "—"
    usd_gbp = safe_val(rates.get("USD_GBP"), ".4f") if rates else "—"
    usd_cad = safe_val(rates.get("USD_CAD"), ".4f") if rates else "—"
    usd_aud = safe_val(rates.get("USD_AUD"), ".4f") if rates else "—"

    # 油价
    oil_current = safe_val(oil.get("current_price"), ".2f") if oil else "—"
    oil_close = safe_val(oil.get("previous_close"), ".2f") if oil else "—"
    oil_unit = oil.get("unit", "USD/桶") if oil else "USD/桶"

    if oil and oil.get("change") is not None:
        change = oil["change"]
        change_pct = oil["change_pct"]
        if change >= 0:
            oil_change_class = "up"
            oil_change_icon = "📈"
            oil_change_str = f"+${change:.2f} (+{change_pct:.2f}%)"
        else:
            oil_change_class = "down"
            oil_change_icon = "📉"
            oil_change_str = f"-${abs(change):.2f} ({change_pct:.2f}%)"
    else:
        oil_change_class = ""
        oil_change_icon = "—"
        oil_change_str = "暂无数据"

    oil_history_html = render_oil_history(oil)
    slang_items_html = render_slang_items(slangs)
    weather_html = render_weather(weather)

    # 替换模板变量
    html_content = template
    replacements = {
        "{{update_date}}": update_date,
        "{{data_time}}": data_time,
        "{{USD_CNY}}": usd_cny,
        "{{USD_EUR}}": usd_eur,
        "{{USD_JPY}}": usd_jpy,
        "{{USD_GBP}}": usd_gbp,
        "{{USD_CAD}}": usd_cad,
        "{{USD_AUD}}": usd_aud,
        "{{oil_current}}": oil_current,
        "{{oil_close}}": oil_close,
        "{{oil_unit}}": oil_unit,
        "{{oil_change_class}}": oil_change_class,
        "{{oil_change_icon}}": oil_change_icon,
        "{{oil_change_str}}": oil_change_str,
        "{{oil_history_html}}": oil_history_html,
        "{{slang_items_html}}": slang_items_html,
        "{{weather_html}}": weather_html,
        "{{github_repo}}": "your-username/us-daily-digest",  # 用户需修改
    }

    for key, value in replacements.items():
        html_content = html_content.replace(key, value)

    # 写入输出文件
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
    )
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"   ✅ 页面已生成: {output_path}")
    print(f"   📏 文件大小: {os.path.getsize(output_path):,} 字节")
    print()
    print("✨ 完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
