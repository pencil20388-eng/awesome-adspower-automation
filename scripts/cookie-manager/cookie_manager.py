"""
AdsPower Cookie Manager
========================
Export and import cookies for AdsPower browser profiles.
Useful for account warmup, backup, migration, and session management.

Usage:
    # Export cookies from a single profile
    python cookie_manager.py export --profile-id h1abc123

    # Export cookies from all profiles in a group
    python cookie_manager.py export --group "My Campaign"

    # Import cookies into a profile from a JSON file
    python cookie_manager.py import --profile-id h1abc123 --file cookies_h1abc123.json

Requirements:
    pip install requests python-dotenv
"""

import argparse
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

EXPORT_DIR = "exported_cookies"


# ─────────────────────────────────────────────
# Export
# ─────────────────────────────────────────────

def export_cookies(profile_id, profile_name=""):
    """
    Export cookies from a profile using the V2 cookie query endpoint.
    The profile does NOT need to be open — this reads stored cookie data.
    """
    resp = requests.get(
        f"{BASE_URL}/api/v2/browser-profile/cookies",
        headers=HEADERS,
        params={"profile_id": profile_id},
        timeout=15,
    ).json()

    if resp.get("code") != 0:
        print(f"  [FAIL] {profile_name or profile_id}: {resp.get('msg', 'Unknown error')}")
        return None

    cookies = resp.get("data", {}).get("cookies", [])

    # Save to file
    os.makedirs(EXPORT_DIR, exist_ok=True)
    label = profile_name or profile_id
    filename = os.path.join(EXPORT_DIR, f"cookies_{label}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)

    print(f"  [OK] {label} — {len(cookies)} cookies → {filename}")
    return filename


def export_group(group_name):
    """Export cookies for every profile in a group."""
    resp = requests.get(
        f"{BASE_URL}/api/v1/user/list",
        headers=HEADERS,
        params={"group_name": group_name, "page": 1, "page_size": 100},
        timeout=10,
    ).json()

    if resp["code"] != 0:
        print(f"[ERROR] Failed to query profiles: {resp['msg']}")
        return

    profiles = resp["data"]["list"]
    if not profiles:
        print(f"[ERROR] No profiles found in group '{group_name}'")
        return

    print(f"[...] Exporting cookies for {len(profiles)} profiles in '{group_name}'")

    for p in profiles:
        export_cookies(p["user_id"], p.get("name", p["user_id"]))
        time.sleep(1.1)  # Rate limit: 1 req/sec

    print(f"\nAll cookies saved to ./{EXPORT_DIR}/")


# ─────────────────────────────────────────────
# Import
# ─────────────────────────────────────────────

def import_cookies(profile_id, cookie_file):
    """
    Import cookies into a profile by updating its configuration.
    The cookie data is written to the profile's stored settings.
    """
    if not os.path.exists(cookie_file):
        print(f"[ERROR] Cookie file not found: {cookie_file}")
        return False

    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    if not cookies:
        print(f"[WARN] Cookie file is empty: {cookie_file}")
        return False

    # Update the profile with cookie data
    payload = {
        "user_id": profile_id,
        "cookie": json.dumps(cookies),
    }

    resp = requests.post(
        f"{BASE_URL}/api/v1/user/update",
        headers=HEADERS,
        json=payload,
        timeout=15,
    ).json()

    if resp.get("code") == 0:
        print(f"  [OK] Imported {len(cookies)} cookies → profile {profile_id}")
        return True
    else:
        print(f"  [FAIL] {profile_id}: {resp.get('msg', 'Unknown error')}")
        return False


def batch_import(folder):
    """
    Import all cookie files from a folder.
    Files must be named: cookies_{profile_id}.json
    """
    if not os.path.isdir(folder):
        print(f"[ERROR] Folder not found: {folder}")
        return

    files = [f for f in os.listdir(folder) if f.startswith("cookies_") and f.endswith(".json")]

    if not files:
        print(f"[ERROR] No cookie files found in {folder}")
        return

    print(f"[...] Importing {len(files)} cookie files from {folder}")

    success = 0
    failed = 0

    for filename in sorted(files):
        # Extract profile_id from filename: cookies_{profile_id}.json
        profile_id = filename.replace("cookies_", "").replace(".json", "")
        filepath = os.path.join(folder, filename)

        if import_cookies(profile_id, filepath):
            success += 1
        else:
            failed += 1
        time.sleep(1.1)

    print(f"\nDone! Success: {success} | Failed: {failed}")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AdsPower Cookie Manager — Export & Import")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Export subcommand
    export_parser = subparsers.add_parser("export", help="Export cookies from profiles")
    export_parser.add_argument("--profile-id", default=None, help="Single profile ID to export")
    export_parser.add_argument("--group", default=None, help="Export all profiles in a group")

    # Import subcommand
    import_parser = subparsers.add_parser("import", help="Import cookies into profiles")
    import_parser.add_argument("--profile-id", default=None, help="Profile ID to import into")
    import_parser.add_argument("--file", default=None, help="Path to cookie JSON file")
    import_parser.add_argument("--folder", default=None, help="Folder of cookie files for batch import")

    args = parser.parse_args()

    if not API_KEY:
        print("[ERROR] API key not set. Edit your .env file.")
        sys.exit(1)

    if args.command == "export":
        if args.profile_id:
            export_cookies(args.profile_id)
        elif args.group:
            export_group(args.group)
        else:
            print("[ERROR] Provide --profile-id or --group")
            sys.exit(1)

    elif args.command == "import":
        if args.folder:
            batch_import(args.folder)
        elif args.profile_id and args.file:
            import_cookies(args.profile_id, args.file)
        else:
            print("[ERROR] Provide --profile-id + --file, or --folder for batch import")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
