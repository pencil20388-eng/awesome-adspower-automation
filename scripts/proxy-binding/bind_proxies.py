"""
AdsPower Batch Proxy Binding
==============================
Bind proxies from a CSV file to existing AdsPower profiles.

Usage:
    python bind_proxies.py --csv proxies.csv

CSV format:
    profile_id,proxy_type,host,port,username,password
    h1abc123,http,1.2.3.4,8080,user1,pass1
    h2def456,socks5,5.6.7.8,1080,user2,pass2

Requirements:
    pip install requests python-dotenv
"""

import argparse
import csv
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ADSPOWER_API_KEY", "")
BASE_URL = os.getenv("ADSPOWER_API_BASE", "http://local.adspower.net:50325")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def update_proxy(profile_id, proxy_type, host, port, username="", password=""):
    """Update proxy settings for a single profile."""
    payload = {
        "user_id": profile_id,
        "user_proxy_config": {
            "proxy_soft": "other",
            "proxy_type": proxy_type,
            "proxy_host": host,
            "proxy_port": str(port),
            "proxy_user": username,
            "proxy_password": password,
        },
    }

    resp = requests.post(
        f"{BASE_URL}/api/v1/user/update",
        headers=HEADERS,
        json=payload,
        timeout=10,
    ).json()

    return resp


def main():
    parser = argparse.ArgumentParser(description="Batch bind proxies to AdsPower profiles")
    parser.add_argument("--csv", required=True, help="Path to CSV file with proxy data")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"[ERROR] File not found: {args.csv}")
        sys.exit(1)

    success = 0
    failed = 0

    with open(args.csv, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[...] Binding proxies for {len(rows)} profiles")

    for row in rows:
        profile_id = row["profile_id"]
        resp = update_proxy(
            profile_id=profile_id,
            proxy_type=row.get("proxy_type", "http"),
            host=row["host"],
            port=row["port"],
            username=row.get("username", ""),
            password=row.get("password", ""),
        )

        if resp.get("code") == 0:
            success += 1
            print(f"  [OK] {profile_id} → {row['host']}:{row['port']}")
        else:
            failed += 1
            print(f"  [FAIL] {profile_id}: {resp.get('msg', 'Unknown error')}")

        time.sleep(1.1)  # Rate limit

    print(f"\nDone! Success: {success} | Failed: {failed}")


if __name__ == "__main__":
    main()
