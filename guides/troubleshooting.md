# Troubleshooting Common AdsPower API Issues

A quick-reference guide for the most frequent problems you'll hit when working with AdsPower's Local API. Each section covers what the error looks like, why it happens, and how to fix it.

---

## "Connection refused" or "Cannot connect"

**What you see:**

```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='local.adspower.net', port=50325)
```

**Why it happens:**
AdsPower is not running, or the API service hasn't started yet.

**Fix:**
1. Open AdsPower on your computer
2. Go to **Automation → API** and check that API status shows **Success**
3. If you're using headless mode, make sure the process is running:
   - Windows: `"C:\Program Files (x86)\AdsPower\AdsPower Global.exe" --headless=true --api-key=YOUR_KEY --api-port=50325`
   - macOS: `"/Applications/AdsPower Global.app/Contents/MacOS/AdsPower Global" --args --headless=true --api-key=YOUR_KEY --api-port=50325`

**Quick test:** Open `http://local.adspower.net:50325/api/v1/status` in your browser. If the API is running, you'll see `{"code":0,"msg":"success"}`.

---

## "API key invalid" / 401 Unauthorized

**What you see:**

```json
{"code": -1, "msg": "Invalid API key"}
```

**Why it happens:**
Your API key is wrong, expired, or not being sent correctly.

**Fix:**
1. In AdsPower, go to **Automation → API** and click **Generate** to get a fresh key
2. Update your `.env` file with the new key — no spaces before or after
3. Make sure your code sends the key in the correct header format:

```python
headers = {"Authorization": "Bearer YOUR_API_KEY_HERE"}
```

**Common mistake:** copying the key with an extra space or newline character. Open your `.env` file in a plain text editor (not Word) to check.

---

## Error 100044: "Waiting for browser to start timeout"

**What you see:**

```json
{"code": -1, "msg": "Error 100044: Waiting for browser to start timeout, please wait"}
```

**Why it happens:**
The browser profile is taking too long to launch. This is usually caused by a slow proxy connection, large cache, or system resource limits.

**Fix:**
1. Check if your proxy is working — a dead or slow proxy will cause the browser to hang
2. Try clearing the profile's cache: AdsPower → right-click the profile → **Clear Cache**
3. Close other running profiles to free up system resources
4. Increase the timeout in your script if you're calling the API programmatically:

```python
# Default timeout might be too short for slow proxies
resp = requests.get(open_url, headers=headers, timeout=60).json()
```

5. If the problem persists, try opening the profile manually in AdsPower first to see if the issue is proxy-related

---

## Error 100001: "Failed to start browser"

**What you see:**

```json
{"code": -1, "msg": "Error 100001: Failed to start browser"}
```

**Why it happens:**
The browser engine failed to initialize. Could be a corrupted profile, incompatible kernel version, or file permission issue.

**Fix:**
1. Try opening the profile manually in AdsPower (not via API). If it also fails there, the issue is with the profile itself
2. Right-click the profile → **Repair** or **Reset** the profile
3. Check your AdsPower version is up to date — older versions may have kernel compatibility issues
4. On Windows, make sure the AdsPower directory is not blocked by antivirus software
5. Check disk space — AdsPower needs space for browser cache files

---

## "Too many requests" / Rate Limit Errors

**What you see:**

```json
{"code": -1, "msg": "Too many requests"}
```

**Why it happens:**
You're calling the API faster than the allowed rate.

**Rate limits by profile count:**

| Profile count | Max frequency |
|---------------|---------------|
| 0 – 200       | 2 requests/sec |
| 200 – 5000    | 5 requests/sec |
| > 5000        | 10 requests/sec |

Profile creation and some other operations are limited to **1 request/sec** regardless of plan.

**Fix:**
Add a delay between API calls in your scripts:

```python
import time

for profile in profiles:
    # Your API call here
    do_something(profile)
    time.sleep(1.1)  # Safe margin above 1 req/sec
```

---

## "Profile not found" / Invalid user_id

**What you see:**

```json
{"code": -1, "msg": "Profile not found"}
```

**Why it happens:**
The `user_id` you're passing doesn't match any existing profile.

**Fix:**
1. The `user_id` is the internal ID assigned when a profile is created — it's NOT the profile name or the number shown in the UI
2. You can find the correct ID by querying the profile list:

```python
resp = requests.get(
    "http://local.adspower.net:50325/api/v1/user/list",
    headers={"Authorization": "Bearer YOUR_KEY"},
    params={"page": 1, "page_size": 10}
).json()

for profile in resp["data"]["list"]:
    print(f"Name: {profile['name']}  ID: {profile['user_id']}")
```

3. If you're using `serial_number` instead of `user_id`, note that `user_id` takes priority when both are provided

---

## Port Changed / API Address Different

**What you see:**
Your script was working yesterday but today it gets "Connection refused."

**Why it happens:**
AdsPower's API port can change between sessions. The default is 50325, but it's not guaranteed to stay the same.

**Fix:**
1. In AdsPower, go to **Automation → API** and check the current API address
2. Or read the port from the `local_api` file programmatically:
   - **Windows:** Check the cache folder in AdsPower settings → `local_api` file
   - **macOS:** `~/Library/Application Support/adspower_global/cwd_global/source/local_api`
   - **Linux:** `~/.config/adspower_global/cwd_global/source/local_api`

```python
import os

def get_api_address():
    """Read the current API address from AdsPower's local_api file."""
    # Adjust path for your OS
    possible_paths = [
        os.path.expanduser("~/.config/adspower_global/cwd_global/source/local_api"),  # Linux
        os.path.expanduser("~/Library/Application Support/adspower_global/cwd_global/source/local_api"),  # macOS
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
    return "http://local.adspower.net:50325"  # Fallback to default
```

---

## Proxy Failure When Opening Browser

**What you see:**
Browser opens but shows a proxy error page, or the API returns a proxy-related error.

**Why it happens:**
The proxy configured for the profile is dead, slow, or has wrong credentials.

**Fix:**
1. Test your proxy independently first (use a tool like curl):

```bash
curl -x http://user:pass@proxy_host:port https://httpbin.org/ip
```

2. In your API call, double-check the proxy config format:

```json
{
  "proxy_soft": "other",
  "proxy_type": "http",
  "proxy_host": "1.2.3.4",
  "proxy_port": "8080",
  "proxy_user": "username",
  "proxy_password": "password"
}
```

3. Common mistakes:
   - `proxy_port` must be a **string**, not a number
   - `proxy_soft` should be `"other"` for third-party proxies
   - `proxy_type` options: `"http"`, `"https"`, `"socks5"`

---

## "Disk space not enough"

**What you see:**

```
The disk space where the cache is located is not enough to open
```

**Why it happens:**
Each browser profile stores cache data locally. If you have many profiles, this adds up fast.

**Fix:**
1. Delete unnecessary cache: AdsPower → select profiles → **Delete Cache**
2. Or via API, use the delete cache endpoint:

```python
resp = requests.post(
    f"{BASE_URL}/api/v1/user/delete-cache",
    headers=headers,
    json={"user_id": profile_id},
).json()
```

3. Move the cache folder to a drive with more space (configurable in AdsPower Settings)

---

## "Service not activated"

**What you see:**

```json
{"code": -1, "msg": "Service not activated"}
```

**Why it happens:**
Your AdsPower subscription has expired or you're on the free plan (which doesn't include API access).

**Fix:**
1. API access requires a paid plan — check your subscription status in AdsPower
2. If you recently renewed, try logging out and back in
3. Team members need API permission explicitly granted by the admin

---

## General Debugging Tips

**Always check the API response.** Every AdsPower API call returns a `code` and `msg`. If `code` is not `0`, something went wrong — and `msg` tells you what.

```python
resp = requests.get(url, headers=headers).json()
if resp["code"] != 0:
    print(f"API Error: {resp['msg']}")
```

**Use the status endpoint as a health check** before running any script:

```python
def is_api_ready():
    try:
        r = requests.get(f"{BASE_URL}/api/v1/status", headers=headers, timeout=5)
        return r.json().get("code") == 0
    except:
        return False
```

**Check AdsPower version compatibility.** Some API endpoints (like V2 endpoints) require newer versions. Update AdsPower if you're getting unexpected errors with newer API calls.

---

Still stuck? Open an [Issue](https://github.com/pencil20388-eng/awesome-adspower-automation/issues) with the full error message and we'll help you debug it.

For more official troubleshooting resources:
- [AdsPower Help Center — Troubleshooting](https://help.adspower.com/docs/troubleshooting)
- [AdsPower Blog — API Troubleshooting Guide](https://www.adspower.com/blog/troubleshooting-common-issues-with-adspower-api-a-complete-guide)
