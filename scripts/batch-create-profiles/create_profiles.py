"""
AdsPower Batch Profile Creator
===============================
Create multiple browser profiles in one command with randomized fingerprints.

Usage:
    python create_profiles.py --count 10
    python create_profiles.py --count 50 --group "My Campaign"
    python create_profiles.py --count 20 --group "US Accounts" --proxy-file proxies.csv

Requirements:
    pip install requests python-dotenv
"""

import argparse
import csv
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY", "")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# --- Rate limit: AdsPower API allows 1 request/sec for profile creation ---
REQUEST_INTERVAL = 1.1


def check_api():
    """Verify API connection."""
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/status", headers=HEADERS, timeout=5)
        return resp.json().get("code") == 0
    except Exception:
        return False


def get_or_create_group(group_name):
    """Find existing group by name, or create a new one. Returns group_id."""
    # Query existing groups
    resp = requests.get(
        f"{BASE_URL}/api/v1/group/list",
        headers=HEADERS,
        params={"page": 1, "page_size": 100},
        timeout=10,
    ).json()

    if resp["code"] == 0:
        for group in resp.get("data", {}).get("list", []):
            if group.get("group_name") == group_name:
                print(f"[OK] Found existing group: {group_name} (ID: {group['group_id']})")
                return group["group_id"]

    # Create new group
    resp = requests.post(
        f"{BASE_URL}/api/v1/group/create",
        headers=HEADERS,
        json={"group_name": group_name},
        timeout=10,
    ).json()

    if resp["code"] == 0:
        group_id = resp["data"]["group_id"]
        print(f"[OK] Created group: {group_name} (ID: {group_id})")
        return group_id
    else:
        print(f"[ERROR] Failed to create group: {resp['msg']}")
        return "0"


def load_proxies(filepath):
    """Load proxies from CSV file. Returns list of proxy configs."""
    proxies = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            proxies.append({
                "proxy_type": row.get("proxy_type", "http"),
                "proxy_host": row.get("host", ""),
                "proxy_port": row.get("port", ""),
                "proxy_user": row.get("username", ""),
                "proxy_password": row.get("password", ""),
                "proxy_soft": "other",
            })
    return proxies


def create_profile(name, group_id="0", proxy_config=None):
    """Create a single browser profile."""
    payload = {
        "name": name,
        "group_id": group_id,
        "fingerprint_config": {
            "automatic_timezone": "1",
            "language": ["en-US", "en"],
        },
    }

    if proxy_config:
        payload["user_proxy_config"] = proxy_config

    resp = requests.post(
        f"{BASE_URL}/api/v1/user/create",
        headers=HEADERS,
        json=payload,
        timeout=15,
    ).json()

    return resp


def main():
    parser = argparse.ArgumentParser(description="Batch create AdsPower profiles")
    parser.add_argument("--count", type=int, required=True, help="Number of profiles to create")
    parser.add_argument("--group", default="Default", help="Group name (default: Default)")
    parser.add_argument("--prefix", default="profile", help="Profile name prefix (default: profile)")
    parser.add_argument("--proxy-file", default=None, help="CSV file with proxy list (optional)")
    args = parser.parse_args()

    # Preflight check
    if not check_api():
        print("[ERROR] Cannot connect to AdsPower API. Is AdsPower running?")
        sys.exit(1)

    print(f"[OK] API connected")
    print(f"[...] Creating {args.count} profiles in group '{args.group}'")

    # Get or create the group
    group_id = get_or_create_group(args.group)

    # Load proxies if provided
    proxies = []
    if args.proxy_file:
        proxies = load_proxies(args.proxy_file)
        print(f"[OK] Loaded {len(proxies)} proxies from {args.proxy_file}")

    # Create profiles
    created = 0
    failed = 0
    results = []

    for i in range(args.count):
        name = f"{args.prefix}_{i + 1:04d}"
        proxy = proxies[i % len(proxies)] if proxies else None

        resp = create_profile(name, group_id, proxy)

        if resp.get("code") == 0:
            profile_id = resp["data"]["id"]
            created += 1
            results.append({"name": name, "id": profile_id})
            print(f"  [{created}/{args.count}] Created: {name} (ID: {profile_id})")
        else:
            failed += 1
            print(f"  [FAIL] {name}: {resp.get('msg', 'Unknown error')}")

        # Rate limit
        time.sleep(REQUEST_INTERVAL)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Done! Created: {created} | Failed: {failed}")

    # Save results
    if results:
        output_file = f"created_profiles_{args.group}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Profile IDs saved to: {output_file}")


if __name__ == "__main__":
    main()
