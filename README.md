[English](./README.md) | [中文文档](./README_CN.md)
# 🚀 Awesome AdsPower Automation

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> A curated collection of ready-to-use scripts, templates, and guides for [AdsPower](https://www.adspower.net/) antidetect browser automation. Copy, paste, run.

Whether you manage 10 accounts or 10,000, this repo gives you **production-ready code** that works out of the box with AdsPower's Local API.

---

## 📦 What's Inside

| Folder | Description | Difficulty |
|--------|-------------|------------|
| [`/scripts/batch-create-profiles`](./scripts/batch-create-profiles) | Create hundreds of browser profiles in one command | ⭐ Beginner |
| [`/scripts/auto-open-close`](./scripts/auto-open-close) | Open, perform tasks, and close browsers automatically | ⭐ Beginner |
| [`/scripts/proxy-binding`](./scripts/proxy-binding) | Batch bind/update proxies across all profiles | ⭐⭐ Intermediate |
| [`/scripts/cookie-manager`](./scripts/cookie-manager) | Import/export cookies for account warmup | ⭐⭐ Intermediate |
| [`/scripts/fingerprint-checker`](./scripts/fingerprint-checker) | Auto-open profiles and verify fingerprint on BrowserScan | ⭐⭐ Intermediate |
| [`/templates/`](./templates) | Reusable config templates (proxy, fingerprint, groups) | ⭐ Beginner |
| [`/guides/`](./guides) | Step-by-step setup guides with screenshots | ⭐ Beginner |

## ⚡ Quick Start (5 minutes)

### Prerequisites

- [AdsPower](https://www.adspower.net/download) installed and running (paid plan with API access)
- [Python 3.8+](https://www.python.org/downloads/) installed
- Your API Key (AdsPower → Automation → API → Generate)

### 1. Clone this repo

```bash
git clone https://github.com/pencil20388-eng/awesome-adspower-automation.git
cd awesome-adspower-automation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API Key

```bash
cp .env.example .env
# Edit .env and paste your API Key
```

### 4. Run your first script

```bash
python scripts/auto-open-close/open_and_visit.py
```

That's it. Your AdsPower profile opens, visits BrowserScan to verify the fingerprint, and closes automatically.

## 🔑 API Key Setup

1. Open AdsPower, go to **Automation → API**
2. Check that API status shows **Success**
3. Click **Generate** to get your API Key
4. Copy the key into your `.env` file

> **Security tip:** Never commit your `.env` file. It's already in `.gitignore`.

## 📂 Script Details

### Batch Create Profiles

Create 100 profiles with randomized fingerprints in under a minute.

```python
# Just edit the number and run
python scripts/batch-create-profiles/create_profiles.py --count 50 --group "My Campaign"
```

### Auto Open & Visit

Open a profile, navigate to any URL, take a screenshot, close.

```python
python scripts/auto-open-close/open_and_visit.py --profile-id xxx --url "https://www.google.com"
```

### Proxy Binding

Bind proxies from a CSV file to profiles in batch.

```python
python scripts/proxy-binding/bind_proxies.py --csv proxies.csv
```

CSV format:
```
profile_id,proxy_type,host,port,username,password
h1abc123,http,1.2.3.4,8080,user1,pass1
h2def456,socks5,5.6.7.8,1080,user2,pass2
```

### Fingerprint Checker

Open each profile, visit BrowserScan, screenshot the result.

```python
python scripts/fingerprint-checker/check_all.py --group "My Campaign"
```

## 📋 Templates

### `templates/proxy_config.json`

```json
{
  "proxy_type": "http",
  "proxy_host": "YOUR_PROXY_HOST",
  "proxy_port": "YOUR_PROXY_PORT",
  "proxy_user": "YOUR_USERNAME",
  "proxy_password": "YOUR_PASSWORD"
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

## 📚 Guides

- [**Getting Started with AdsPower API (Zero to Hero)**](./guides/getting-started.md) — Complete beginner guide, from installing Python to running your first automation
- [**Proxy Setup Best Practices**](./guides/proxy-setup.md) — How to choose and configure proxies for multi-account management
- [**Selenium + AdsPower Integration**](./guides/selenium-integration.md) — Connect Selenium to AdsPower profiles for advanced automation
- [**Playwright + AdsPower Integration**](./guides/playwright-integration.md) — Use Playwright for faster, more reliable browser automation
- [**Troubleshooting Common API Issues**](./guides/troubleshooting.md) — Fixes for the most frequent problems

## 🔗 Official Resources

- 🌐 [AdsPower Official Website](https://www.adspower.net/)
- 📖 [Local API Documentation](https://localapi-doc-en.adspower.net/)
- 💬 [Help Center](https://help.adspower.net/)
- 📝 [AdsPower Blog](https://www.adspower.net/blog)

## 🤝 Contributing

Found a bug? Have a useful script? PRs are welcome!

1. Fork this repo
2. Create your branch (`git checkout -b feature/my-script`)
3. Commit your changes (`git commit -m 'Add: new script for XYZ'`)
4. Push (`git push origin feature/my-script`)
5. Open a Pull Request

## ⚠️ Disclaimer

This repository is for educational and legitimate business use only. Always comply with the terms of service of any platform you interact with. The authors are not responsible for any misuse of these tools.

## 📄 License

[MIT](LICENSE) — Use it, modify it, share it.

---

**⭐ If this repo saved you time, give it a star!** It helps others find it too.
