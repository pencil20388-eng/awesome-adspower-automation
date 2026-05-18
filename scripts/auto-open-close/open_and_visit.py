"""
AdsPower Auto Open & Visit
===========================
Opens an AdsPower browser profile, visits a URL, takes a screenshot, and closes.

Usage:
    python open_and_visit.py --profile-id YOUR_PROFILE_ID
    python open_and_visit.py --profile-id YOUR_PROFILE_ID --url "https://www.google.com"

Requirements:
    pip install requests selenium python-dotenv
"""

import argparse
import os
import sys
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY", "")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")


def check_api_status():
    """Check if AdsPower API is running."""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/v1/status",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=5,
        )
        data = resp.json()
        if data.get("code") == 0:
            print("[OK] AdsPower API is running")
            return True
        else:
            print(f"[ERROR] API returned: {data.get('msg', 'Unknown error')}")
            return False
    except requests.ConnectionError:
        print("[ERROR] Cannot connect to AdsPower. Is it running?")
        print(f"        Tried: {BASE_URL}")
        return False


def open_browser(profile_id):
    """Open an AdsPower browser profile and return connection info."""
    url = f"{BASE_URL}/api/v1/browser/start?user_id={profile_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    print(f"[...] Opening profile: {profile_id}")
    resp = requests.get(url, headers=headers, timeout=30).json()

    if resp["code"] != 0:
        print(f"[ERROR] Failed to open browser: {resp['msg']}")
        sys.exit(1)

    print("[OK] Browser opened successfully")
    return resp["data"]


def close_browser(profile_id):
    """Close an AdsPower browser profile."""
    url = f"{BASE_URL}/api/v1/browser/stop?user_id={profile_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    resp = requests.get(url, headers=headers, timeout=10).json()
    if resp["code"] == 0:
        print("[OK] Browser closed")
    else:
        print(f"[WARN] Close returned: {resp['msg']}")


def main():
    parser = argparse.ArgumentParser(description="Open AdsPower profile and visit a URL")
    parser.add_argument("--profile-id", required=True, help="AdsPower profile user_id")
    parser.add_argument("--url", default="https://www.browserscan.net/", help="URL to visit (default: BrowserScan)")
    parser.add_argument("--wait", type=int, default=5, help="Seconds to wait before closing (default: 5)")
    parser.add_argument("--screenshot", action="store_true", help="Take a screenshot before closing")
    args = parser.parse_args()

    # Step 1: Check API
    if not check_api_status():
        sys.exit(1)

    # Step 2: Open browser
    browser_data = open_browser(args.profile_id)

    try:
        # Step 3: Connect Selenium
        chrome_driver = browser_data["webdriver"]
        debug_address = browser_data["ws"]["selenium"]

        service = Service(executable_path=chrome_driver)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debug_address)

        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"[OK] Connected to browser: {driver.title}")

        # Step 4: Visit URL
        print(f"[...] Navigating to: {args.url}")
        driver.get(args.url)
        print(f"[OK] Page loaded: {driver.title}")

        # Step 5: Optional screenshot
        if args.screenshot:
            filename = f"screenshot_{args.profile_id}.png"
            driver.save_screenshot(filename)
            print(f"[OK] Screenshot saved: {filename}")

        # Step 6: Wait
        print(f"[...] Waiting {args.wait} seconds...")
        time.sleep(args.wait)

        # Step 7: Close
        driver.quit()

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        close_browser(args.profile_id)


if __name__ == "__main__":
    main()
