
# 📬 Medium → Freedium Daily Mailer

Automatically receive **Medium articles in your inbox** as **Freedium links**, every morning — **fully automated, free, and serverless**.

No subscriptions. No copy-paste.

---

## ✨ What this project does

* 📩 Reads **Medium emails** from your Gmail
* 🔗 Extracts **article links**
* 🪞 Converts them to **Freedium** (paywall-free)
* 🖼️ Preserves **title, image, and excerpt**
* 🏷️ Marks processed emails to **avoid duplicates**
* ⏰ Runs **daily via GitHub Actions**
* 📬 Sends you a **clean HTML email digest**

---

## 🧠 How it works

```
Medium Email
     ↓
Gmail API
     ↓
Extract article links
     ↓
Convert → Freedium
     ↓
Send HTML email
     ↓
Label emails as processed
```

---

## 🚀 Quick Start (For New Users)

### 1️⃣ Fork this repository

Click the **Fork** button at the top-right of this page to create your own copy.

### 2️⃣ Create Google OAuth credentials

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a new project (or use existing)
* Enable **Gmail API** ([Quick link](https://console.cloud.google.com/apis/library/gmail.googleapis.com))
* **Configure OAuth Consent Screen**:
  - Go to **OAuth consent screen**
  - Choose **External** user type
  - **Publishing status**: 
    - ⚠️ **Testing** = Refresh token expires in **7 days** (need to regenerate weekly)
    - ✅ **Production** = Refresh token lasts **indefinitely** (recommended)
  - Add your email as test user (if using Testing mode)
* Go to **Credentials → Create Credentials → OAuth 2.0 Client ID**
* Choose **Desktop App**
* Download the `credentials.json` file

💡 **Recommendation**: Use **Production** mode to avoid weekly token regeneration

### 3️⃣ Generate `token.json` locally

Clone your forked repo and run:

```bash
git clone https://github.com/YOUR_USERNAME/Medium-Freedium.git
cd Medium-Freedium
pip install -r requirements.txt

# Set your email address
export RECIPIENT_EMAIL="your-email@gmail.com"

# Run the script (will open browser for authentication)
python main.py
```

This will:
* Open a browser for Google sign-in
* Ask you to authorize Gmail access  
* Generate `token.json` file

### 4️⃣ Create Gmail label

In Gmail, create a label named exactly:
```
PROCESSED_BY_BOT
```

Left sidebar → **More → Create new label** → Enter name → Create

### 5️⃣ Add secrets to GitHub ⚠️ REQUIRED

* Go to your forked repo → **Settings → Secrets and variables → Actions**
* Click **New repository secret** and add **BOTH** of these:

| Secret Name        | Value                              | Required |
| ------------------ | ---------------------------------- | -------- |
| `GMAIL_TOKEN`      | Full contents of `token.json` file | ✅ Yes   |
| `RECIPIENT_EMAIL`  | Your email address (e.g., `you@gmail.com`) | ✅ Yes   |

To get the contents of `token.json`:
```bash
cat token.json
# Copy the entire output (including { and })
```

⚠️ **Important:** Do **not** commit `token.json` or `credentials.json` to the repository!

### 6️⃣ Enable GitHub Actions

* Go to **Actions** tab in your forked repo
* Click **I understand my workflows, go ahead and enable them**

✅ **Done!** The workflow will run daily at 08:30 IST, or you can trigger it manually.

---

## ⏰ Schedule

By default, the workflow runs **once per day**:

* **08:30 AM IST** (03:00 UTC)
* Controlled via GitHub Actions `cron`

You can also trigger it manually:
```
GitHub → Actions → Daily Medium Freedium Mailer → Run workflow
```

---

## 🔑 Testing vs Production Configuration

### Google OAuth Publishing Status (IMPORTANT)

When creating OAuth credentials in Google Cloud Console:

| Publishing Status | Refresh Token Lifespan | Regeneration Needed |
| ----------------- | ---------------------- | ------------------- |
| **Testing** | 7 days | Every week |
| **Production** | Indefinitely | Rarely/Never |

**Testing Mode**:
- Refresh token expires after **7 days**
- Must run `python main.py` locally every week and update `GMAIL_TOKEN` secret
- Only added test users can authenticate

**Production Mode** (Recommended):
- Refresh token lasts indefinitely
- No weekly regeneration needed
- Anyone can authenticate (but only you have credentials)

### Local Testing (Development)
```bash
export RECIPIENT_EMAIL="your@gmail.com"
python main.py
```
- Uses `credentials.json` + `token.json` from local directory
- Token auto-refreshes if not expired
- Regenerates token if missing/expired

### Production (GitHub Actions)
```yaml
env:
  GMAIL_TOKEN: ${{ secrets.GMAIL_TOKEN }}
  RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
```
- Uses GitHub repository secrets
- Token auto-refreshes (if refresh token valid)
- Both secrets are **required**

---

## 📁 Project structure

```
.
├── .github/
│   └── workflows/
│       └── main.yml             # GitHub Actions workflow
├── main.py                      # Core script
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Python project config
├── credentials.json.example     # OAuth credentials template
├── .gitignore                   # Git ignore rules
├── .python-version              # Python version specification
└── README.md                    # This file
```

---

## 🏷️ How the Gmail label works

The script uses a Gmail label to avoid duplicate processing:

```
PROCESSED_BY_BOT
```

* Create it once in Gmail (left sidebar → Create label)
* The script resolves the label **by name**
* Each Medium email is processed only once
* Safe to re-run without sending duplicates

---

## 📬 When will I receive emails?

* If Medium sends an email **before 08:30 AM** → included the same day
* If Medium sends an email **after 08:30 AM** → included the next day
* The script checks the last **24 hours** of emails
* Nothing is missed
* No duplicate emails are ever sent

---

## 🛠️ Tech stack

* **Python 3.11+**
* **Gmail API** (OAuth 2.0)
* **GitHub Actions** (free tier)
* **BeautifulSoup4** (HTML parsing)
* **Pydantic** (data validation)

No database. No server. No paid services.

---

## 🔒 Security & Privacy

* Your Gmail credentials stay with you (OAuth tokens in GitHub Secrets)
* No third-party services involved
* Open source — audit the code yourself
* GitHub Secrets are encrypted and not exposed in logs
* `credentials.json` and `token.json` are gitignored

---

## ⚙️ Configuration

You can customize the behavior by editing [main.py](main.py):

| Variable            | Default                | Description                |
| ------------------- | ---------------------- | -------------------------- |
| `PROCESSED_LABEL`   | `PROCESSED_BY_BOT`     | Gmail label for tracking   |
| `query`             | `newer_than:1d`        | Time window for emails     |
| `maxResults`        | `10`                   | Max emails to process      |
| Email subject       | `Today's Medium Articles` | Subject line of digest  |

---

## 🚀 Why this approach works well

* ✅ **Free forever** — no hosting costs
* ✅ **Serverless** — GitHub Actions does the work
* ✅ **No background polling** — runs on schedule
* ✅ **Safe re-runs** — label system prevents duplicates
* ✅ **Simple and reliable** — minimal dependencies
**Testing mode**: Refresh token expires in 7 days → Regenerate weekly
- **Production mode**: Refresh token lasts indefinitely → Rarely expires
- **To regenerate**: Run `python main.py` locally → Update `GMAIL_TOKEN` secret in GitHub

### OAuth app is in Testing mode (weekly expiration)
Switch to Production mode in Google Cloud Console → OAuth consent screen → Publishing status → Publish appL` as repository secret

### "Missing GMAIL_TOKEN secret"
Add `GMAIL_TOKEN` as a GitHub repository secret (full contents of `token.json`)

### "Label 'PROCESSED_BY_BOT' not found"
Create the label in Gmail exactly as shown (case-sensitive)

### "No new Medium emails"
Script processes last 24 hours only. Wait for Medium to send emails or test with older time range.

### Token expired / Invalid credentials
- Token usually auto-refreshes (has refresh token built-in)
- If completely expired: Run `python main.py` locally → Regenerate `token.json` → Update `GMAIL_TOKEN` secret
- Refresh tokens typically last 6+ months
### "No new Medium emails"
The script only processes emails from the last 24 hours. Make sure you have Medium emails in your inbox.

### Token expired
If your token expires, regenerate it by running `python main.py` locally again and updating the `GMAIL_TOKEN` secret.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

* Report bugs
* Suggest features
* Submit pull requests
* Improve documentation

---

## 📄 License

MIT — use it, fork it, improve it.

---

## 🙏 Credits

* **Freedium** for the paywall bypass service
* **Medium** for the original content
* **Google Gmail API** for email access

---

**Enjoy your daily Medium articles without paywalls! 📚✨**
