# 🚀 AdsPower 指纹浏览器自动化脚本合集

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

[English](./README.md) | **中文**

> 一套开箱即用的 [AdsPower](https://www.adspower.net/) 指纹浏览器自动化脚本、模板和教程。复制，粘贴，运行。

不管你管 10 个账号还是 10000 个，这个仓库给你的都是**拿来就能跑的代码**，直接对接 AdsPower Local API。

---

## 📦 仓库里有什么

| 文件夹 | 干什么用 | 难度 |
|--------|----------|------|
| [`/scripts/batch-create-profiles`](./scripts/batch-create-profiles) | 一条命令批量创建几百个浏览器配置文件 | ⭐ 入门 |
| [`/scripts/auto-open-close`](./scripts/auto-open-close) | 自动打开浏览器、执行任务、关闭 | ⭐ 入门 |
| [`/scripts/proxy-binding`](./scripts/proxy-binding) | 批量给所有配置文件绑定/更新代理 | ⭐⭐ 进阶 |
| [`/scripts/cookie-manager`](./scripts/cookie-manager) | 导入导出 Cookie，用于账号养号 | ⭐⭐ 进阶 |
| [`/scripts/fingerprint-checker`](./scripts/fingerprint-checker) | 自动打开配置文件并在 BrowserScan 上验证指纹 | ⭐⭐ 进阶 |
| [`/templates/`](./templates) | 可复用的配置模板（代理、指纹、分组） | ⭐ 入门 |
| [`/guides/`](./guides) | 从零开始的图文教程 | ⭐ 入门 |

## ⚡ 5 分钟快速开始

### 前置条件

- 已安装并运行 [AdsPower](https://www.adspower.net/download)（需付费版，有 API 权限）
- 已安装 [Python 3.8+](https://www.python.org/downloads/)
- 拿到你的 API Key（AdsPower → 自动化 → API → 生成）

### 1. 克隆仓库

```bash
git clone https://github.com/pencil20388-eng/awesome-adspower-automation.git
cd awesome-adspower-automation
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
cp .env.example .env
# 打开 .env 文件，把你的 API Key 粘贴进去
```

### 4. 跑第一个脚本

```bash
python scripts/auto-open-close/open_and_visit.py
```

就这么简单。你的 AdsPower 配置文件会自动打开浏览器，访问 BrowserScan 验证指纹，然后自动关闭。

## 🔑 API Key 怎么拿

1. 打开 AdsPower，进入 **自动化 → API**
2. 确认 API 状态显示 **成功**
3. 点 **生成** 拿到你的 API Key
4. 把 Key 复制到 `.env` 文件里

> **安全提醒：** 永远不要把 `.env` 文件提交到 Git。`.gitignore` 已经帮你排除了。

## 📂 脚本详细说明

### 批量创建配置文件

一分钟内创建 100 个带随机指纹的配置文件。

```python
# 改个数字就能跑
python scripts/batch-create-profiles/create_profiles.py --count 50 --group "我的活动"
```

### 自动打开并访问

打开某个配置文件，访问指定网址，截图，关闭。

```python
python scripts/auto-open-close/open_and_visit.py --profile-id xxx --url "https://www.google.com"
```

### 批量绑定代理

从 CSV 文件批量给配置文件绑定代理。

```python
python scripts/proxy-binding/bind_proxies.py --csv proxies.csv
```

CSV 格式：
```
profile_id,proxy_type,host,port,username,password
h1abc123,http,1.2.3.4,8080,user1,pass1
h2def456,socks5,5.6.7.8,1080,user2,pass2
```

### 指纹检查器

逐个打开配置文件，访问 BrowserScan，把检测结果截图保存。

```python
python scripts/fingerprint-checker/check_all.py --group "我的活动"
```

## 📋 配置模板

### `templates/proxy_config.json`

```json
{
  "proxy_type": "http",
  "proxy_host": "你的代理地址",
  "proxy_port": "你的代理端口",
  "proxy_user": "你的用户名",
  "proxy_password": "你的密码"
}
```

### `templates/fingerprint_config.json`

```json
{
  "automatic_timezone": "1",
  "language": ["en-US", "en"],
  "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
```

## 📚 教程

- [**AdsPower API 从零开始（小白教程）**](./guides/getting-started.md) — 从装 Python 到跑通第一个自动化脚本
- [**代理设置最佳实践**](./guides/proxy-setup.md) — 怎么选代理、怎么配
- [**Selenium + AdsPower 集成指南**](./guides/selenium-integration.md) — 用 Selenium 连接 AdsPower 做高级自动化
- [**Playwright + AdsPower 集成指南**](./guides/playwright-integration.md) — 用 Playwright 做更快更稳的浏览器自动化
- [**常见问题排查**](./guides/troubleshooting.md) — 最常遇到的坑和解决办法

## 🔗 官方资源

- 🌐 [AdsPower 官网](https://www.adspower.net/)
- 📖 [Local API 文档](https://localapi-doc-en.adspower.net/)
- 💬 [帮助中心](https://help.adspower.net/)
- 📝 [AdsPower 博客](https://www.adspower.net/blog)

## 🤝 参与贡献

发现 bug 了？有好用的脚本想分享？欢迎提 PR！

1. Fork 这个仓库
2. 创建你的分支 (`git checkout -b feature/my-script`)
3. 提交改动 (`git commit -m 'Add: 新脚本 XXX'`)
4. 推送 (`git push origin feature/my-script`)
5. 发起 Pull Request

## ⚠️ 免责声明

本仓库仅用于教育和合法商业用途。使用时请遵守相关平台的服务条款。作者不对任何滥用行为负责。

## 📄 开源协议

[MIT](LICENSE) — 随便用，随便改，随便分享。

---

**⭐ 觉得有用就给个 Star 吧！** 能帮更多人看到这个仓库。
