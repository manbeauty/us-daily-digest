"""
🇺🇸 美国每日资讯日报 V2 — 主入口
编排 12 个数据模块 → 渲染 HTML → 输出 index.html
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import beijing_now, utc_now_str
from exchange_rate import get_exchange_rate_data
from oil_gas_price import get_oil_gas_data
from temperature_map import fetch_all_temperatures
from social_trends import get_social_data
from news import get_news_data
from hot_products import get_hot_products
from ope_market import get_ope_data
from warehouse import get_warehouse_data
from ecommerce_policy import get_ecommerce_policy_data
from tariff_policy import get_tariff_data
from company_news import get_company_data


def load_template():
    path = os.path.join(os.path.dirname(__file__), "template.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_exchange_chart(data):
    """构建汇率 ECharts 图表脚本"""
    history = data.get("history", [])
    current = data.get("current", {})
    if not history:
        return "console.log('No exchange history data');"

    dates = json.dumps([h["date"][5:10] for h in history])
    rates = json.dumps([h["rate"] for h in history])
    cny = current.get("USD_CNY", 0)

    return f"""
    var exchangeChart = echarts.init(document.getElementById('chart-exchange'));
    exchangeChart.setOption({{
        tooltip: {{ trigger: 'axis' }},
        title: {{ text: 'USD/CNY 近 1 年走势', left: 'center', textStyle: {{fontSize: 14}} }},
        xAxis: {{ type: 'category', data: {dates}, axisLabel: {{rotate: 45, fontSize: 10}} }},
        yAxis: {{ type: 'value', name: '汇率' }},
        series: [{{
            data: {rates}, type: 'line', smooth: true,
            lineStyle: {{color: '#1a73e8', width: 2}},
            areaStyle: {{color: 'rgba(26,115,232,0.1)'}},
            markPoint: {{ data: [{{type: 'max', name: '最高'}}, {{type: 'min', name: '最低'}}] }},
            markLine: {{ data: [{{yAxis: {cny}, label: {{formatter: '当前: {cny}'}}}}] }}
        }}],
        grid: {{left: '3%', right: '4%', bottom: '15%', containLabel: true}}
    }});
    """


def build_oil_chart(data):
    """构建油价 ECharts 图表脚本"""
    crude = data.get("crude", {})
    history = crude.get("history", [])
    if not history:
        return "console.log('No oil history data');"

    dates = json.dumps([h["date"][5:10] for h in history])
    prices = json.dumps([h["close"] for h in history])
    current = crude.get("current_price", 0)

    return f"""
    var oilChart = echarts.init(document.getElementById('chart-oil'));
    oilChart.setOption({{
        tooltip: {{ trigger: 'axis' }},
        title: {{ text: 'WTI 原油近 1 年走势', left: 'center', textStyle: {{fontSize: 14}} }},
        xAxis: {{ type: 'category', data: {dates}, axisLabel: {{rotate: 45, fontSize: 10}} }},
        yAxis: {{ type: 'value', name: 'USD/桶' }},
        series: [{{
            data: {prices}, type: 'line', smooth: true,
            lineStyle: {{color: '#e37400', width: 2}},
            areaStyle: {{color: 'rgba(227,116,0,0.1)'}},
            markPoint: {{ data: [{{type: 'max', name: '最高'}}, {{type: 'min', name: '最低'}}] }},
            markLine: {{ data: [{{yAxis: {current}, label: {{formatter: '${current}'}}}}] }}
        }}],
        grid: {{left: '3%', right: '4%', bottom: '15%', containLabel: true}}
    }});
    """


def build_temp_map_script(temps):
    """构建温度地图 ECharts 脚本"""
    if not temps:
        return "console.log('No temperature data');"

    map_data = []
    for t in temps:
        map_data.append({"name": t["state"], "value": t["temperature_f"]})

    data_json = json.dumps(map_data)

    return f"""
    fetch('https://cdn.jsdelivr.net/npm/echarts-map@1.2.0/js/us.js')
    .then(function(r) {{ return r.text(); }})
    .then(function(usMap) {{
        eval(usMap);
        var tempChart = echarts.init(document.getElementById('chart-temp-map'));
        tempChart.setOption({{
            title: {{ text: '美国各州实时温度 (°F)', left: 'center', textStyle: {{fontSize: 14}} }},
            tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}}°F' }},
            visualMap: {{
                min: 0, max: 110, left: 'left', top: 'bottom',
                text: ['高温 🔥', '低温 ❄️'],
                inRange: {{ color: ['#313695','#4575b4','#74add1','#abd9e9','#fee090','#fdae61','#f46d43','#d73027'] }},
                calculable: true
            }},
            series: [{{
                name: '温度', type: 'map', map: 'US', roam: true,
                label: {{ show: true, fontSize: 10 }},
                data: {data_json}
            }}]
        }});
    }});
    """


def format_news_tab(news_data):
    html = ""
    categories = [
        ("🇺🇸 美国十大新闻", news_data.get("us", [])),
        ("🇨🇳 中国十大新闻", news_data.get("china", [])),
        ("🌐 国际十大新闻", news_data.get("international", [])),
    ]
    for title, items in categories:
        html += f'<div class="card"><h2>{title}</h2><div class="news-list">'
        for i, item in enumerate(items[:10]):
            url = item.get("url", "#")
            html += f'''
            <div class="news-item">
              <span class="news-rank">{i+1}</span>
              <a href="{url}" target="_blank" rel="noopener">{item["title"]}</a>
              <span class="news-meta">{item.get("source", "")} · {item.get("published", "")}</span>
              <p class="news-desc">{item.get("description", "")}</p>
            </div>'''
        html += "</div></div>"
    return html


def format_social_tab(data):
    html = ""
    # Trends
    trends = data.get("trends", [])
    html += '<div class="card"><h2>📈 Google Trends 今日热搜</h2>'
    if trends:
        html += '<ol class="rank-list">'
        for t in trends[:10]:
            html += f'<li><strong>{t["keyword"]}</strong></li>'
        html += '</ol>'
    else:
        html += '<p class="no-data">暂无数据</p>'
    html += '</div>'

    # Reddit
    reddit = data.get("reddit", [])
    html += '<div class="card"><h2>🔴 Reddit 热门讨论</h2>'
    if reddit:
        html += '<div class="news-list">'
        for i, r in enumerate(reddit[:10]):
            url = r.get("url", "#")
            html += f'''
            <div class="news-item">
              <span class="news-rank">{i+1}</span>
              <a href="{url}" target="_blank" rel="noopener">{r["title"]}</a>
              <span class="news-meta">r/{r.get("subreddit", "")} · 👍 {r.get("score", 0)}</span>
            </div>'''
        html += '</div>'
    else:
        html += '<p class="no-data">暂无数据</p>'
    html += '</div>'

    # Slang
    slang = data.get("slang", [])
    html += '<div class="card"><h2>🗣️ 美国网络流行语</h2>'
    if slang:
        html += '<div class="slang-list">'
        for s in slang:
            html += f'''
            <div class="slang-item">
              <div class="slang-word">{s["word"]}</div>
              <div class="slang-meaning">{s["meaning"]}</div>
              <div class="slang-example">💬 {s["example"]}</div>
            </div>'''
        html += '</div>'
    else:
        html += '<p class="no-data">暂无数据</p>'
    html += '</div>'

    return html


def format_products_tab(data):
    html = ""
    platforms = [
        ("Amazon", data.get("amazon", [])),
        ("Walmart", data.get("walmart", [])),
        ("TikTok Shop", data.get("tiktok", [])),
    ]
    for name, items in platforms:
        html += f'<div class="card"><h2>🛒 {name} TOP10 热销</h2>'
        if items:
            html += '<ol class="rank-list">'
            for item in items[:10]:
                html += f'<li>{item.get("name", "")}</li>'
            html += '</ol>'
        else:
            html += '<p class="no-data">暂无数据</p>'
        html += '</div>'
    return html


def format_simple_news_tab(data, icon="📰"):
    news = data.get("news", [])
    html = f'<div class="card"><h2>{icon} 最新资讯</h2>'
    if not news:
        html += '<p class="no-data">暂无数据</p></div>'
        return html

    html += '<div class="news-list">'
    for i, item in enumerate(news[:15]):
        url = item.get("url", "#")
        company = item.get("company", "")
        company_tag = f'<span class="company-tag">{company}</span>' if company else ""
        html += f'''
        <div class="news-item">
          <span class="news-rank">{i+1}</span>
          {company_tag}
          <a href="{url}" target="_blank" rel="noopener">{item["title"]}</a>
          <span class="news-meta">{item.get("source", "")} · {item.get("date", "")}</span>
          <p class="news-desc">{item.get("summary", "")}</p>
        </div>'''
    html += '</div></div>'
    return html


def safe_val(value, fmt=".4f"):
    if value is None:
        return "—"
    try:
        return format(float(value), fmt)
    except (ValueError, TypeError):
        return str(value)


def main():
    print("=" * 50)
    print("🇺🇸 美国每日资讯日报 V2 生成器")
    print("=" * 50)

    now = beijing_now()
    print(f"📅 {now.strftime('%Y-%m-%d %H:%M')} 北京时间\n")

    # === 采集模块 ===
    print("📡 1/11 汇率数据...")
    exchange = get_exchange_rate_data()

    print("📡 2/11 原油+汽油数据...")
    oil_gas = get_oil_gas_data()

    print("📡 3/11 温度数据 (50州)...")
    temps = fetch_all_temperatures()

    print("📡 4/11 社交热点...")
    social = get_social_data()

    print("📡 5/11 新闻...")
    news = get_news_data()

    print("📡 6/11 电商热销...")
    products = get_hot_products()

    print("📡 7/11 OPE市场...")
    ope = get_ope_data()

    print("📡 8/11 海外仓...")
    warehouse = get_warehouse_data()

    print("📡 9/11 电商政策...")
    ec_policy = get_ecommerce_policy_data()

    print("📡 10/11 关税政策...")
    tariff = get_tariff_data()

    print("📡 11/11 企业动态...")
    companies = get_company_data()

    # === 渲染 ===
    print("\n📝 生成 HTML...")
    template = load_template()

    # 汇率
    current_rate = exchange.get("current", {})
    usd_cny = safe_val(current_rate.get("USD_CNY", ""), ".4f")
    usd_eur = safe_val(current_rate.get("USD_EUR", ""), ".4f")
    usd_jpy = safe_val(current_rate.get("USD_JPY", ""), ".2f")
    usd_gbp = safe_val(current_rate.get("USD_GBP", ""), ".4f")
    usd_cad = safe_val(current_rate.get("USD_CAD", ""), ".4f")
    usd_aud = safe_val(current_rate.get("USD_AUD", ""), ".4f")
    usd_chf = safe_val(current_rate.get("USD_CHF", ""), ".4f")

    # 油价
    crude = oil_gas.get("crude", {})
    gas = oil_gas.get("gas", {})
    crude_price = safe_val(crude.get("current_price"), ".2f")
    gas_regular = safe_val(gas.get("regular"), ".3f")
    gas_midgrade = safe_val(gas.get("midgrade"), ".3f")
    gas_premium = safe_val(gas.get("premium"), ".3f")
    gas_diesel = safe_val(gas.get("diesel"), ".3f")

    # 涨跌
    change_val = crude.get("change")
    change_pct = crude.get("change_pct")
    if change_val is not None and change_pct is not None:
        if change_val >= 0:
            rate_change_class = "up"
            rate_change_icon = "📈"
            rate_change = f"+{change_val:.2f} (+{change_pct:.2f}%)"
        else:
            rate_change_class = "down"
            rate_change_icon = "📉"
            rate_change = f"{change_val:.2f} ({change_pct:.2f}%)"
    else:
        rate_change_class = ""
        rate_change_icon = ""
        rate_change = "暂无数据"

    # ECharts scripts
    exchange_chart_script = build_exchange_chart(exchange)
    oil_chart_script = build_oil_chart(oil_gas)
    temp_map_script = build_temp_map_script(temps)

    # Tab HTML
    tab_social_html = format_social_tab(social)
    tab_news_html = format_news_tab(news)
    tab_products_html = format_products_tab(products)
    tab_ope_html = format_simple_news_tab(ope, "🌿")
    tab_warehouse_html = format_simple_news_tab(warehouse, "📦")
    tab_ecpolicy_html = format_simple_news_tab(ec_policy, "🏪")
    tab_tariff_html = format_simple_news_tab(tariff, "🛃")
    tab_companies_html = format_simple_news_tab(companies, "🏢")

    # Replace
    replacements = {
        "{{update_date}}": now.strftime("%Y年%m月%d日 %A"),
        "{{data_time}}": utc_now_str(),
        "{{USD_CNY}}": usd_cny,
        "{{USD_EUR}}": usd_eur,
        "{{USD_JPY}}": usd_jpy,
        "{{USD_GBP}}": usd_gbp,
        "{{USD_CAD}}": usd_cad,
        "{{USD_AUD}}": usd_aud,
        "{{USD_CHF}}": usd_chf,
        "{{rate_change}}": rate_change,
        "{{rate_change_class}}": rate_change_class,
        "{{rate_change_icon}}": rate_change_icon,
        "{{crude_price}}": crude_price,
        "{{gas_regular}}": gas_regular,
        "{{gas_midgrade}}": gas_midgrade,
        "{{gas_premium}}": gas_premium,
        "{{gas_diesel}}": gas_diesel,
        "{{exchange_chart_script}}": exchange_chart_script,
        "{{oil_chart_script}}": oil_chart_script,
        "{{temp_map_script}}": temp_map_script,
        "{{tab_social_html}}": tab_social_html,
        "{{tab_news_html}}": tab_news_html,
        "{{tab_products_html}}": tab_products_html,
        "{{tab_ope_html}}": tab_ope_html,
        "{{tab_warehouse_html}}": tab_warehouse_html,
        "{{tab_ecpolicy_html}}": tab_ecpolicy_html,
        "{{tab_tariff_html}}": tab_tariff_html,
        "{{tab_companies_html}}": tab_companies_html,
    }

    html_content = template
    for key, value in replacements.items():
        html_content = html_content.replace(key, str(value))

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ 页面生成: {output_path}")
    print(f"📏 大小: {os.path.getsize(output_path):,} 字节")
    print("=" * 50)


if __name__ == "__main__":
    main()
