# Playwright + AdsPower Integration Guide

Playwright is a modern browser automation framework from Microsoft. Compared to Selenium, it's faster, more reliable, and has better support for modern web features. This guide shows you how to connect Playwright to AdsPower browser profiles.

---

## Why Playwright Over Selenium?

| | Selenium | Playwright |
|---|---|---|
| Speed | Slower (JSON Wire Protocol) | Faster (CDP / WebSocket) |
| Auto-wait | Manual waits needed | Built-in smart waiting |
| Modern web | Can struggle with SPAs | Handles SPAs well |
| Screenshots | Basic | Full-page, element-level |
| Network control | Limited | Intercept, mock, block requests |
| API style | Verbose | Cleaner, more readable |

Both work with AdsPower. If you're starting fresh, Playwright is the better choice. If you already have Selenium scripts, they'll work fine — no need to rewrite.

## How It Works

Same principle as Selenium: AdsPower opens a browser profile with its fingerprint and proxy configured, then exposes a WebSocket endpoint. Playwright connects to that endpoint instead of launching its own browser.

```
Your Script → AdsPower API → Opens profile (fingerprint + proxy ready)
                                    ↓
            Playwright connects via CDP WebSocket
                                    ↓
            You control the browser: navigate, click, scrape, screenshot
```

## Prerequisites

- [AdsPower](https://www.adspower.net/download) installed and running (paid plan with API access)
- [Python 3.8+](https://www.python.org/downloads/)
- At least one browser profile created in AdsPower
- Your API Key (AdsPower → Automation → API → Generate)

## Step 1: Install Playwright

```bash
pip install playwright requests python-dotenv
playwright install chromium
```

The second command downloads the Chromium browser binary that Playwright needs. You only run it once.

## Step 2: Set Up Your API Key

Create a `.env` file in your project folder:

```
ADSPOWER_API_KEY=your_api_key_here
ADSPOWER_API_BASE=http://local.adspower.net:50325
```

## Step 3: Basic Script — Synchronous Version

This is the simplest way to get started. It opens a profile, visits a website, takes a screenshot, and closes.

```python
import os
import sys
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

PROFILE_ID = "YOUR_PROFILE_ID"  # Replace with your actual profile ID

# 1. Open the browser via AdsPower API
resp = requests.get(
    f"{BASE_URL}/api/v1/browser/start?user_id={PROFILE_ID}",
    headers=HEADERS,
    timeout=30,
).json()

if resp["code"] != 0:
    print(f"Failed to open browser: {resp['msg']}")
    sys.exit(1)

# 2. Get the WebSocket endpoint
ws_endpoint = resp["data"]["ws"]["puppeteer"]
print(f"Connected to: {ws_endpoint}")

# 3. Connect Playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws_endpoint)
    context = browser.contexts[0]  # Use the existing context
    page = context.pages[0] if context.pages else context.new_page()

    # 4. Do your automation
    page.goto("https://www.browserscan.net/")
    page.wait_for_load_state("networkidle")
    print(f"Page title: {page.title()}")

    # Take a screenshot
    page.screenshot(path="screenshot.png", full_page=True)
    print("Screenshot saved!")

    browser.close()

# 5. Close the browser via API
requests.get(
    f"{BASE_URL}/api/v1/browser/stop?user_id={PROFILE_ID}",
    headers=HEADERS,
)
print("Done!")
```

**Key difference from Selenium:** Playwright connects via `ws_puppeteer` (WebSocket), not the Selenium debug address. In the API response, use `resp["data"]["ws"]["puppeteer"]`, not `resp["data"]["ws"]["selenium"]`.

## Step 4: Async Version (Recommended for Multiple Profiles)

The async version is faster when you need to process many profiles, because it can handle concurrent operations more efficiently.

```python
import asyncio
import os
import sys
import requests
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


async def automate_profile(profile_id, profile_name, url):
    """Open one profile, visit a URL, screenshot, close."""

    # Open browser
    resp = requests.get(
        f"{BASE_URL}/api/v1/browser/start?user_id={profile_id}",
        headers=HEADERS,
        timeout=30,
    ).json()

    if resp["code"] != 0:
        print(f"  [FAIL] {profile_name}: {resp['msg']}")
        return

    ws_endpoint = resp["data"]["ws"]["puppeteer"]

    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()

            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            print(f"  [OK] {profile_name}: {await page.title()}")

            # Screenshot
            await page.screenshot(path=f"screenshots/{profile_name}.png", full_page=True)

            await browser.close()

    except Exception as e:
        print(f"  [ERROR] {profile_name}: {e}")

    finally:
        requests.get(
            f"{BASE_URL}/api/v1/browser/stop?user_id={profile_id}",
            headers=HEADERS,
        )


async def main():
    # Get all profiles in a group
    resp = requests.get(
        f"{BASE_URL}/api/v1/user/list",
        headers=HEADERS,
        params={"group_name": "My Campaign", "page": 1, "page_size": 100},
    ).json()

    profiles = resp["data"]["list"]
    print(f"Processing {len(profiles)} profiles...")

    os.makedirs("screenshots", exist_ok=True)

    # Process one at a time (AdsPower rate limit)
    for p in profiles:
        await automate_profile(p["user_id"], p["name"], "https://www.browserscan.net/")
        await asyncio.sleep(2)  # Cool down


asyncio.run(main())
```

## Step 5: Common Tasks

### Click and fill forms

```python
# Click a button (Playwright auto-waits for it to be visible)
page.click("button.submit")

# Fill a form field
page.fill("#username", "my_username")
page.fill("#password", "my_password")
page.click("button[type='submit']")

# Select from dropdown
page.select_option("select#country", "US")
```

### Wait for elements

```python
# Wait for a specific element to appear
page.wait_for_selector(".results-loaded")

# Wait for navigation after clicking
page.click("a.next-page")
page.wait_for_load_state("networkidle")
```

### Extract data

```python
# Get text content
title = page.text_content("h1")
print(title)

# Get all items in a list
items = page.query_selector_all(".product-card")
for item in items:
    name = item.text_content()
    print(name)

# Get an attribute
link = page.get_attribute("a.profile-link", "href")
```

### Block unnecessary resources (speed up loading)

```python
# Block images and stylesheets to load pages faster
async def block_resources(route):
    if route.request.resource_type in ["image", "stylesheet", "font"]:
        await route.abort()
    else:
        await route.continue_()

await page.route("**/*", block_resources)
await page.goto("https://example.com")
```

### Take screenshots

```python
# Full page screenshot
page.screenshot(path="full_page.png", full_page=True)

# Element screenshot
element = page.query_selector(".main-content")
element.screenshot(path="element.png")

# Screenshot with specific viewport
page.set_viewport_size({"width": 1920, "height": 1080})
page.screenshot(path="desktop_view.png")
```

## Selenium vs Playwright: Connection Difference

The API response gives you both connection methods. Use the right one for your framework:

```python
resp = requests.get(open_url, headers=HEADERS).json()

# For Selenium — use the selenium debug address
selenium_address = resp["data"]["ws"]["selenium"]
# Example: "127.0.0.1:xxxx"

# For Playwright — use the puppeteer WebSocket
playwright_ws = resp["data"]["ws"]["puppeteer"]
# Example: "ws://127.0.0.1:xxxx/devtools/browser/xxxxxx"
```

## Common Issues

**"Browser is not connected" error**
→ The WebSocket endpoint might have expired. Make sure you connect to the browser immediately after opening it. If there's a long delay between `browser/start` and `connect_over_cdp`, the connection might time out.

**"No context available" error**
→ This happens when the browser is still initializing. Add a short delay after connecting:

```python
browser = p.chromium.connect_over_cdp(ws_endpoint)
import time; time.sleep(1)  # Wait for context to initialize
context = browser.contexts[0]
```

**Page loads but elements can't be found**
→ Playwright's auto-wait usually handles this, but some SPAs need extra time. Use explicit waits:

```python
page.wait_for_selector(".target-element", timeout=10000)
```

**"Execution context was destroyed" error**
→ The page navigated while you were trying to interact with it. Use `wait_for_load_state` after navigation:

```python
page.goto("https://example.com")
page.wait_for_load_state("domcontentloaded")
```

**Playwright can't find the Chromium binary**
→ Run `playwright install chromium` again. This is Playwright's own browser binary, separate from AdsPower's browser.

---

## Next Steps

- **Selenium integration** → [`selenium-integration.md`](./selenium-integration.md)
- **Account warmup** → [`/scripts/account-warmup`](../scripts/account-warmup)
- **Troubleshooting** → [`troubleshooting.md`](./troubleshooting.md)

Questions? Open an [Issue](https://github.com/pencil20388-eng/awesome-adspower-automation/issues).
