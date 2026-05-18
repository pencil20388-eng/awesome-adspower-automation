"""
AdsPower Fingerprint Checker
==============================
Opens each profile in a group, visits BrowserScan.net, takes a screenshot.
Useful for verifying fingerprint isolation across profiles.

Usage:
    python check_all.py --group "My Campaign"
    python check_all.py --profile-id h1abc123

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

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY", "")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

BROWSERSCAN_URL = "https://www.browserscan.net/"
SCREENSHOT_DIR = "fingerprint_screenshots"


def get_profiles(group_name=None):
    """Query profiles, optionally filtered by group name."""
    params = {"page": 1, "page_size": 100}
    if group_name:
        params["group_name"] = group_name

    resp = requests.get(
        f"{BASE_URL}/api/v1/user/list",
        headers=HEADERS,
        params=params,
        timeout=10,
    ).json()

    if resp["code"] == 0:
        return resp["data"]["list"]
    else:
        print(f"[ERROR] Failed to query profiles: {resp['msg']}")
        return []


def check_fingerprint(profile_id, profile_name=""):
    """Open profile, visit BrowserScan, screenshot, close."""
    # Open browser
    resp = requests.get(
        f"{BASE_URL}/api/v1/browser/start?user_id={profile_id}",
        headers=HEADERS,
        timeout=30,
    ).json()

    if resp["code"] != 0:
        print(f"  [FAIL] Cannot open {profile_name}: {resp['msg']}")
        return False

    try:
        browser_data = resp["data"]
        chrome_driver = browser_data["webdriver"]
        debug_address = browser_data["ws"]["selenium"]

        service = Service(executable_path=chrome_driver)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debug_address)

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(BROWSERSCAN_URL)

        # Wait for page to fully load and fingerprint scan to complete
        time.sleep(8)

        # Screenshot
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        filename = os.path.join(SCREENSHOT_DIR, f"{profile_name}_{profile_id}.png")
        driver.save_screenshot(filename)
        print(f"  [OK] {profile_name} — screenshot saved: {filename}")

        driver.quit()

    except Exception as e:
        print(f"  [ERROR] {profile_name}: {e}")

    finally:
        # Always close browser
        requests.get(
            f"{BASE_URL}/api/v1/browser/stop?user_id={profile_id}",
            headers=HEADERS,
            timeout=10,
        )
        time.sleep(2)  # Wait before opening next profile

    return True


def main():
    parser = argparse.ArgumentParser(description="Check fingerprints for AdsPower profiles")
    parser.add_argument("--group", default=None, help="Group name to check")
    parser.add_argument("--profile-id", default=None, help="Single profile ID to check")
    args = parser.parse_args()

    if args.profile_id:
        print(f"[...] Checking single profile: {args.profile_id}")
        check_fingerprint(args.profile_id, "single")
    elif args.group:
        profiles = get_profiles(args.group)
        if not profiles:
            print("[ERROR] No profiles found in this group")
            sys.exit(1)

        print(f"[...] Checking {len(profiles)} profiles in group '{args.group}'")
        for p in profiles:
            check_fingerprint(p["user_id"], p.get("name", p["user_id"]))
    else:
        print("[ERROR] Provide either --group or --profile-id")
        sys.exit(1)

    print(f"\nScreenshots saved to: ./{SCREENSHOT_DIR}/")


if __name__ == "__main__":
    main()
