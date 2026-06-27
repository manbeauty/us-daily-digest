# 🇺🇸 美国每日资讯日报

> 每天早上 9:00（北京时间），自动获取最新资讯并生成精美日报页面。

## 📋 包含内容

| 模块 | 内容 | 数据源 |
|------|------|--------|
| 💱 **美元汇率** | USD/CNY 等6种主要货币汇率 | open.er-api.com |
| 🛢️ **油价趋势** | WTI 原油期货价格 + 近7日走势 | Yahoo Finance |
| 🗣️ **美国俚语** | 10条地道俚语和网络流行语 + 中文解释 + 例句 | Urban Dictionary + Reddit + 备用词库 |
| 🌤️ **一周天气** | 美国10大州首府7天天气预报 | National Weather Service |

## 🚀 部署步骤

### 前提条件
- 一个 [GitHub](https://github.com) 账号（免费）

### 一键部署

1. **在 GitHub 上创建仓库**
   - 登录 GitHub
   - 点击右上角 `+` → `New repository`
   - 仓库名: `us-daily-digest`
   - 设为 **Public**
   - 不要勾选任何初始化选项
   - 点击 `Create repository`

2. **在本地推送代码**

   ```bash
   cd F:\AI\us-daily-digest
   git init
   git add .
   git commit -m "🎉 初始化美国每日资讯日报"
   git branch -M main
   git remote add origin https://github.com/你的用户名/us-daily-digest.git
   git push -u origin main
   ```

3. **开启 GitHub Pages**
   - 进入仓库 → `Settings` → `Pages`
   - `Source` 选 `GitHub Actions`
   - 无需其他配置

4. **手动触发测试**
   - 进入仓库 → `Actions` → `🇺🇸 每日资讯日报`
   - 点击 `Run workflow` → `Run workflow`
   - 等待约 2 分钟后，你的日报就会自动部署

5. **查看日报**
   - 打开 `https://你的用户名.github.io/us-daily-digest/`
   - 以后每天 9:00 自动更新

## 🛠️ 本地测试

如果你本地有 Python 3.7+，可以直接运行测试：

```bash
cd F:\AI\us-daily-digest
python src/main.py
```

生成的页面在 `output/index.html`，浏览器打开即可查看。

## ⚙️ 自定义

### 修改推送时间
编辑 `.github/workflows/daily-digest.yml` 中的 cron 表达式：
```yaml
- cron: '0 1 * * *'  # UTC 1:00 = 北京时间 9:00
```

### 增加/减少州的数量
编辑 `states.json` 添加或删除州数据（需要提供经纬度坐标）。

### 修改页面样式
直接编辑 `src/template.html` 中的 CSS 样式。

## 📄 许可证

MIT
