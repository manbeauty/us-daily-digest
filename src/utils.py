"""
工具函数模块 — 通用工具函数，供所有采集模块使用
"""

import json
import os
import time
import hashlib
from datetime import datetime, timezone, timedelta


def get_data_dir():
    """获取 data 缓存目录路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def beijing_now():
    """获取当前北京时间"""
    return datetime.now(timezone(timedelta(hours=8)))


def utc_now_str():
    """获取 UTC 时间字符串"""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


def safe_request(url, headers=None, timeout=15, retries=2):
    """
    安全的 HTTP 请求，含重试和异常处理
    返回: response.text 或 None
    """
    import urllib.request
    import urllib.error
    import ssl

    ssl_context = ssl.create_default_context()
    default_headers = {
        "User-Agent": "USDailyDigest/2.0 (Mozilla/5.0 compatible; daily-news-bot)"
    }

    if headers:
        default_headers.update(headers)

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=default_headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            print(f"[utils] 请求失败: {url} - {e}")
            return None


def cache_data(filename, data):
    """
    将数据缓存到 data/ 目录
    data 为可 JSON 序列化的对象
    """
    cache_dir = get_data_dir()
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_cache(filename, max_age_hours=24):
    """
    加载缓存数据，超过 max_age_hours 返回 None
    """
    path = os.path.join(get_data_dir(), filename)
    if not os.path.exists(path):
        return None

    # 检查文件年龄
    mtime = os.path.getmtime(path)
    age_hours = (time.time() - mtime) / 3600
    if age_hours > max_age_hours:
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def append_history(cache_file, new_entry, max_entries=365):
    """
    向历史数据文件追加一条新记录
    """
    history = load_cache(cache_file, max_age_hours=9999) or []
    history.append(new_entry)
    # 保留最近 max_entries 条
    if len(history) > max_entries:
        history = history[-max_entries:]
    cache_data(cache_file, history)
    return history