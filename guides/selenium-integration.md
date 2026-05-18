[selenium-integration.md](https://github.com/user-attachments/files/27952567/selenium-integration.md)
# Selenium + AdsPower Integration Guide

Connect Selenium to AdsPower browser profiles for advanced automation. This guide covers everything from installation to running your first automated task.

---

## How It Works

When you open an AdsPower profile via API, it returns a debug interface address. Selenium connects to this address instead of launching its own browser. This means your automation runs inside a fully configured antidetect environment — unique fingerprint, proxy, cookies, and all.

```
Your Script → AdsPower API → Opens profile with fingerprint + proxy
                                    ↓
            Selenium connects to the running browser via debug port
                                    ↓
            You control the browser: visit pages, click, type, scrape
```

The key advantage: you don't need to configure fingerprints or proxies in your Selenium code. AdsPower handles all of that. Your script just focuses on what to do inside the browser.

## Prerequisites

- [AdsPower](https://www.adspower.com/download) installed and running (paid plan with API access)
- [Python 3.8+](https://www.python.org/downloads/)
- At least one browser profile created in AdsPower
- Your API Key (AdsPower → Automation → API → Generate)

## Step 1: Install Selenium

```bash
pip install selenium requests python-dotenv
```

You do NOT need to download ChromeDriver separately. AdsPower provides its own WebDriver that matches the browser kernel version. The API returns the path to it automatically.

## Step 2: Set Up Your API Key

Create a `.env` file in your project folder:

```
ADSPOWER_API_KEY=your_api_key_here
ADSPOWER_API_BASE=http://local.adspower.net:50325
```

## Step 3: Basic Script — Open Profile and Visit a URL

This is the minimal working example. It opens an AdsPower profile, connects Selenium to it, visits a website, and closes.

```python
import os
import sys
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

PROFILE_ID = "YOUR_PROFILE_ID"  # Replace with your actual profile ID

# 1. Open the browser via API
resp = requests.get(
    f"{BASE_URL}/api/v1/browser/start?user_id={PROFILE_ID}",
    headers=HEADERS,
    timeout=30,
).json()

if resp["code"] != 0:
    print(f"Failed to open browser: {resp['msg']}")
    sys.exit(1)

# 2. Get connection info
chrome_driver = resp["data"]["webdriver"]
debug_address = resp["data"]["ws"]["selenium"]

# 3. Connect Selenium to the running browser
service = Service(executable_path=chrome_driver)
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", debug_address)

driver = webdriver.Chrome(service=service, options=chrome_options)

# 4. Do your automation
driver.get("https://www.browserscan.net/")
print(f"Page title: {driver.title}")
time.sleep(5)

# 5. Clean up
driver.quit()
requests.get(
    f"{BASE_URL}/api/v1/browser/stop?user_id={PROFILE_ID}",
    headers=HEADERS,
)
print("Done!")
```

Replace `YOUR_PROFILE_ID` with an actual profile ID from your AdsPower. You can find it in AdsPower's profile list, or query it via API:

```python
resp = requests.get(
    f"{BASE_URL}/api/v1/user/list",
    headers=HEADERS,
    params={"page": 1, "page_size": 10},
).json()

for p in resp["data"]["list"]:
    print(f"{p['name']} → {p['user_id']}")
```

## Step 4: Interact with Pages

Once Selenium is connected, you can do everything you'd normally do: find elements, click buttons, fill forms, extract data.

### Click a button

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Wait for an element and click it
button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.submit"))
)
button.click()
```

### Fill a form

```python
username_field = driver.find_element(By.ID, "username")
username_field.clear()
username_field.send_keys("my_username")

password_field = driver.find_element(By.ID, "password")
password_field.clear()
password_field.send_keys("my_password")

driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
```

### Extract text

```python
heading = driver.find_element(By.TAG_NAME, "h1")
print(heading.text)
```

### Take a screenshot

```python
driver.save_screenshot("screenshot.png")
```

## Step 5: Loop Through Multiple Profiles

This is where AdsPower + Selenium gets powerful. You can automate the same task across dozens of profiles.

```python
import os
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_profiles(group_name):
    """Get all profile IDs in a group."""
    resp = requests.get(
        f"{BASE_URL}/api/v1/user/list",
        headers=HEADERS,
        params={"group_name": group_name, "page": 1, "page_size": 100},
    ).json()
    return resp["data"]["list"]

def automate_profile(profile_id, profile_name, task_url):
    """Open one profile, do the task, close it."""
    # Open
    resp = requests.get(
        f"{BASE_URL}/api/v1/browser/start?user_id={profile_id}",
        headers=HEADERS,
        timeout=30,
    ).json()

    if resp["code"] != 0:
        print(f"  [FAIL] {profile_name}: {resp['msg']}")
        return

    try:
        service = Service(executable_path=resp["data"]["webdriver"])
        options = Options()
        options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
        driver = webdriver.Chrome(service=service, options=options)

        # --- YOUR TASK HERE ---
        driver.get(task_url)
        print(f"  [OK] {profile_name}: {driver.title}")
        time.sleep(3)
        # --- END TASK ---

        driver.quit()
    except Exception as e:
        print(f"  [ERROR] {profile_name}: {e}")
    finally:
        requests.get(
            f"{BASE_URL}/api/v1/browser/stop?user_id={profile_id}",
            headers=HEADERS,
        )
        time.sleep(2)  # Cool down between profiles

# Run
profiles = get_profiles("My Campaign")
print(f"Processing {len(profiles)} profiles...")

for p in profiles:
    automate_profile(p["user_id"], p["name"], "https://www.google.com")
```

## Selenium Version Compatibility

AdsPower provides its own WebDriver binary matched to the browser kernel. This avoids the common "ChromeDriver version mismatch" headache. However, your Selenium Python package version still matters.

| Selenium version | Notes |
|---|---|
| 3.x | Uses `webdriver.Chrome(chrome_driver, options=...)` syntax |
| 4.x+ | Uses `webdriver.Chrome(service=Service(...), options=...)` syntax |

All examples in this guide use **Selenium 4.x** syntax. If you're on Selenium 3.x, change:

```python
# Selenium 4.x (recommended)
service = Service(executable_path=chrome_driver)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Selenium 3.x (legacy)
driver = webdriver.Chrome(chrome_driver, options=chrome_options)
```

## Common Issues

**"WebDriver not found" error**
→ The WebDriver path returned by the API might have changed. Print `resp["data"]["webdriver"]` to check the actual path.

**Browser opens but Selenium can't connect**
→ The debug port might take a moment to initialize. Add a short sleep between opening the browser and connecting:

```python
resp = requests.get(open_url, headers=HEADERS).json()
time.sleep(2)  # Wait for debug port
# Then connect Selenium
```

**"Session not created" error**
→ Usually a Selenium/ChromeDriver version mismatch. Since AdsPower provides its own WebDriver, make sure you're using the path from `resp["data"]["webdriver"]`, not a locally installed ChromeDriver.

**Profile opens but proxy fails**
→ Check proxy configuration in AdsPower first. The API doesn't validate proxy connectivity — it just applies whatever proxy is configured for the profile.

## Firefox Profiles

If your AdsPower profile uses FlowerBrowser (Firefox-based), the connection method is different:

```python
from selenium.webdriver.firefox.service import Service as FirefoxService

resp = requests.get(open_url, headers=HEADERS).json()

firefox_driver = resp["data"]["webdriver"]
marionette_port = resp["data"]["marionette_port"]

service = FirefoxService(
    executable_path=firefox_driver,
    service_args=["--marionette-port", str(marionette_port), "--connect-existing"],
)
driver = webdriver.Firefox(service=service)
```

---

## Next Steps

- **Playwright integration** → [`playwright-integration.md`](./playwright-integration.md) (faster, more reliable alternative to Selenium)
- **Batch operations** → [`/scripts/batch-create-profiles`](../scripts/batch-create-profiles)
- **Troubleshooting** → [`troubleshooting.md`](./troubleshooting.md)

Questions? Open an [Issue](https://github.com/pencil20388-eng/awesome-adspower-automation/issues).
