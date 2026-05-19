"""
AdsPower Account Warmup
========================
Simulate human-like browsing behavior across multiple profiles.
Useful for warming up new accounts to build browsing history and avoid detection.

Each profile will:
  1. Open the browser
  2. Visit a list of popular websites
  3. Scroll randomly, pause between pages
  4. Close the browser

Usage:
    # Warm up all profiles in a group
    python warmup.py --group "My Campaign"

    # Warm up a single profile
    python warmup.py --profile-id h1abc123

    # Custom number of sites per profile (default: 5)
    python warmup.py --group "My Campaign" --sites 8

Requirements:
    pip install requests selenium python-dotenv
"""

import argparse
import os
import random
import sys
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY", "")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# ─────────────────────────────────────────────
# Websites to visit during warmup
# Mix of categories to look like a real person browsing
# ─────────────────────────────────────────────
WARMUP_SITES = [
    # News
    "https://www.bbc.com",
    "https://www.reuters.com",
    "https://news.ycombinator.com",
    # Shopping
    "https://www.amazon.com",
    "https://www.ebay.com",
    # Social
    "https://www.reddit.com",
    "https://www.pinterest.com",
    # Tech
    "https://www.github.com",
    "https://stackoverflow.com",
    "https://www.producthunt.com",
    # Video
    "https://www.youtube.com",
    # Reference
    "https://www.wikipedia.org",
    "https://www.medium.com",
    # Weather / Utility
    "https://www.weather.com",
    "https://www.google.com/maps",
    # Search
    "https://www.google.com",
    "https://www.bing.com",
]


def human_delay(min_sec=2, max_sec=6):
    """Wait a random amount of time to simulate human behavior."""
    time.sleep(random.uniform(min_sec, max_sec))


def random_scroll(driver):
    """Scroll the page in a human-like pattern."""
    # Scroll down 2-5 times
    scroll_count = random.randint(2, 5)
    for _ in range(scroll_count):
        scroll_amount = random.randint(200, 600)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 2.0))

    # Sometimes scroll back up
    if random.random() > 0.6:
        driver.execute_script("window.scrollBy(0, -300);")
        time.sleep(random.uniform(0.5, 1.5))


def random_mouse_move(driver):
    """Move the mouse to a random position on the page."""
    try:
        body = driver.find_element("tag name", "body")
        action = ActionChains(driver)
        x_offset = random.randint(50, 400)
        y_offset = random.randint(50, 300)
        action.move_to_element_with_offset(body, x_offset, y_offset).perform()
    except Exception:
        pass  # Not critical if mouse move fails


def search_something(driver):
    """Sometimes do a Google search to build search history."""
    search_terms = [
        "best restaurants near me",
        "weather today",
        "how to learn python",
        "latest tech news",
        "online shopping deals",
        "travel destinations 2026",
        "productivity tips",
        "new movies this week",
    ]

    try:
        driver.get("https://www.google.com")
        human_delay(1, 3)

        search_box = driver.find_element("name", "q")
        term = random.choice(search_terms)

        # Type like a human (character by character with random delays)
        for char in term:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

        human_delay(0.5, 1.5)
        search_box.send_keys(Keys.RETURN)
        human_delay(2, 4)
        random_scroll(driver)
    except Exception:
        pass  # Not critical


def warmup_profile(profile_id, profile_name, num_sites):
    """Run a full warmup session for one profile."""
    print(f"\n  [{profile_name}] Starting warmup...")

    # Open browser
    resp = requests.get(
        f"{BASE_URL}/api/v1/browser/start?user_id={profile_id}",
        headers=HEADERS,
        timeout=30,
    ).json()

    if resp["code"] != 0:
        print(f"  [{profile_name}] FAIL: {resp['msg']}")
        return False

    try:
        # Connect Selenium
        service = Service(executable_path=resp["data"]["webdriver"])
        options = Options()
        options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
        driver = webdriver.Chrome(service=service, options=options)

        # Pick random sites
        sites = random.sample(WARMUP_SITES, min(num_sites, len(WARMUP_SITES)))

        # Sometimes start with a Google search
        if random.random() > 0.5:
            print(f"  [{profile_name}] Doing a Google search...")
            search_something(driver)

        # Visit each site
        for i, url in enumerate(sites, 1):
            try:
                print(f"  [{profile_name}] ({i}/{len(sites)}) Visiting {url}")
                driver.get(url)
                human_delay(3, 8)

                # Simulate human interactions
                random_scroll(driver)
                random_mouse_move(driver)
                human_delay(1, 3)

            except Exception as e:
                print(f"  [{profile_name}] Skipping {url}: {e}")
                continue

        print(f"  [{profile_name}] Warmup complete ({len(sites)} sites visited)")
        driver.quit()
        return True

    except Exception as e:
        print(f"  [{profile_name}] ERROR: {e}")
        return False

    finally:
        # Always close the browser
        requests.get(
            f"{BASE_URL}/api/v1/browser/stop?user_id={profile_id}",
            headers=HEADERS,
            timeout=10,
        )
        # Cool down between profiles
        human_delay(3, 6)


def get_profiles(group_name=None):
    """Get profile list, optionally filtered by group."""
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
        print(f"[ERROR] {resp['msg']}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Warm up AdsPower profiles with human-like browsing")
    parser.add_argument("--group", default=None, help="Group name to warm up")
    parser.add_argument("--profile-id", default=None, help="Single profile ID")
    parser.add_argument("--sites", type=int, default=5, help="Number of sites to visit per profile (default: 5)")
    parser.add_argument("--shuffle", action="store_true", help="Randomize profile order")
    args = parser.parse_args()

    if not API_KEY:
        print("[ERROR] Set ADSPOWER_API_KEY in your .env file")
        sys.exit(1)

    if args.profile_id:
        profiles = [{"user_id": args.profile_id, "name": args.profile_id}]
    elif args.group:
        profiles = get_profiles(args.group)
    else:
        print("[ERROR] Provide --group or --profile-id")
        sys.exit(1)

    if not profiles:
        print("[ERROR] No profiles found")
        sys.exit(1)

    if args.shuffle:
        random.shuffle(profiles)

    total = len(profiles)
    success = 0

    print(f"[START] Warming up {total} profiles, {args.sites} sites each")
    print(f"        Estimated time: {total * args.sites * 8 // 60} - {total * args.sites * 15 // 60} minutes")

    for p in profiles:
        if warmup_profile(p["user_id"], p.get("name", p["user_id"]), args.sites):
            success += 1

    print(f"\n[DONE] {success}/{total} profiles warmed up successfully")


if __name__ == "__main__":
    main()
