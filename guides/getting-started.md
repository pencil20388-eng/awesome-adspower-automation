[getting-started.md](https://github.com/user-attachments/files/27951130/getting-started.md)
# Getting Started with AdsPower API — Zero to Hero

This guide takes you from zero to running your first AdsPower automation script. No prior coding experience needed.

## What You'll Learn

By the end of this guide, you will:

- Have Python installed on your computer
- Understand how AdsPower's Local API works
- Run a script that opens a browser profile automatically

Time needed: ~15 minutes.

## Step 1: Install Python

### Windows

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python 3.x version
3. Run the installer
4. **Important:** Check the box that says "Add Python to PATH" before clicking Install

To verify, open Command Prompt and type:

```bash
python --version
```

You should see something like `Python 3.12.x`.

### macOS

Open Terminal and run:

```bash
brew install python3
```

If you don't have Homebrew, install it first from [brew.sh](https://brew.sh/).

## Step 2: Set Up AdsPower API

1. Open AdsPower on your computer
2. Go to **Automation → API**
3. Make sure the API status shows **Success**
4. Click **Generate** to create an API Key
5. Copy the API Key somewhere safe — you'll need it soon

The default API address is:

```
http://local.adspower.net:50325/
```

You can verify it's working by opening that URL in your browser. You should see:

```json
{"code":0,"msg":"success"}
```

## Step 3: Download This Repo

Option A — If you have Git installed:

```bash
git clone https://github.com/pencil20388-eng/awesome-adspower-automation.git
cd awesome-adspower-automation
```

Option B — No Git? Just click the green **Code** button on GitHub, then **Download ZIP**, and unzip it.

## Step 4: Install Dependencies

Open your terminal/command prompt, navigate to the repo folder, and run:

```bash
pip install -r requirements.txt
```

This installs the Python libraries the scripts need (requests, selenium, python-dotenv).

## Step 5: Configure Your API Key

```bash
cp .env.example .env
```

Open the `.env` file in any text editor and replace the placeholder:

```
ADSPOWER_API_KEY=your_actual_api_key_here
```

## Step 6: Run Your First Script

Make sure AdsPower is running, and you have at least one browser profile created.

Find the profile ID of any existing profile (you can see it in AdsPower's profile list), then run:

```bash
python scripts/auto-open-close/open_and_visit.py --profile-id YOUR_PROFILE_ID
```

You should see:

1. The browser opens automatically
2. It navigates to BrowserScan.net
3. Waits 5 seconds
4. Closes the browser

Congratulations — you just ran your first automation! 🎉

## How Does It Work?

Here's what happens behind the scenes:

```
Your Script  →  HTTP Request  →  AdsPower Local API  →  Browser Opens
                                                      ↓
Your Script  ←  Response      ←  AdsPower Local API  ←  Browser Ready
                                                      ↓
Your Script  →  Selenium/Playwright connects to the browser
                                                      ↓
                Perform any action: visit URLs, click buttons, fill forms...
```

The Local API runs on your computer at `http://local.adspower.net:50325/`. When you call it, AdsPower handles all the fingerprint configuration, proxy setup, and browser launching. Your script just tells it what to do.

## Key API Endpoints

| What You Want to Do | Endpoint | Method |
|---|---|---|
| Check API status | `/api/v1/status` | GET |
| Open a browser | `/api/v1/browser/start?user_id=XXX` | GET |
| Close a browser | `/api/v1/browser/stop?user_id=XXX` | GET |
| Create a new profile | `/api/v1/user/create` | POST |
| Update a profile | `/api/v1/user/update` | POST |
| Query profiles | `/api/v1/user/list` | GET |
| Create a group | `/api/v1/group/create` | POST |

All requests need the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## What's Next?

- **Batch create profiles** → [`/scripts/batch-create-profiles`](../scripts/batch-create-profiles)
- **Bind proxies to profiles** → [`/scripts/proxy-binding`](../scripts/proxy-binding)
- **Integrate with Selenium** → [`selenium-integration.md`](./selenium-integration.md)
- **Integrate with Playwright** → [`playwright-integration.md`](./playwright-integration.md)

## Common Mistakes

**"Connection refused" error**
→ AdsPower is not running. Open AdsPower first, then run the script.

**"API key invalid" error**
→ Check your `.env` file. Make sure there are no extra spaces around the key.

**"Profile not found" error**
→ Double-check the profile ID. You can find it in AdsPower → Profile list → the ID column.

**"Port 50325 is not responding"**
→ The port may have changed. In AdsPower, go to Automation → API to see the current address.

---

Questions? Open an [Issue](https://github.com/pencil20388-eng/awesome-adspower-automation/issues) and we'll help.
