
# 📬 Medium → Freedium Daily Mailer

Automatically receive **Medium articles in your inbox** as **Freedium links**, every morning — **fully automated, free, and serverless**.

No subscriptions.
No copy-paste

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

## ⏰ Schedule

By default, the workflow runs **once per day**:

* **08:30 AM IST**
* Controlled via GitHub Actions `cron`

You can also trigger it manually from the GitHub Actions UI.

---

## 📁 Project structure

```
.
├── Project/
│   └── main.py              # Core script (no FastAPI server)
├── .github/
│   └── workflows/
│       └── daily-medium.yml # GitHub Actions workflow
├── README.md
```

---

## 🔐 Authentication (one-time setup)

### 1️⃣ Create Google OAuth credentials

* Enable **Gmail API**
* Download `credentials.json`

### 2️⃣ Generate `token.json` locally

Run once on your machine:

```bash
python Project/main.py
```

This will:

* Open a browser
* Ask you to sign in
* Generate `token.json`

---

### 3️⃣ Add token to GitHub Secrets

* Repo → **Settings → Secrets → Actions**
* Add secret:

| Name          | Value                         |
| ------------- | ----------------------------- |
| `GMAIL_TOKEN` | Full contents of `token.json` |

⚠️ Do **not** commit `token.json`.

---

## 🏷️ Gmail label

The script uses a Gmail label to avoid duplicate processing:

```
PROCESSED_BY_BOT
```

* Create it once in Gmail (left sidebar → Create label)
* The script resolves the label **by ID**
* Each Medium email is processed only once

---

## 🧪 Manual run

You can trigger the workflow anytime:

```
GitHub → Actions → Daily Medium Freedium Mailer → Run workflow
```

If new Medium emails exist, you’ll receive a mail immediately.

---

## 📬 When will I receive emails?

* If Medium sends an email **before 08:30 AM** → included the same day
* If Medium sends an email **after 08:30 AM** → included the next day
* Nothing is missed thanks to a 24-hour sliding window
* No duplicate emails are ever sent

---

## 🛠️ Tech stack

* Python 3.11
* Gmail API
* GitHub Actions
* BeautifulSoup
* Pydantic

No database.
No server.
No paid services.

---

## 🚀 Why this approach works well

* ✅ Free forever
* ✅ Serverless
* ✅ No background polling
* ✅ Safe re-runs
* ✅ Simple and reliable

---

## 🧾 License

MIT — use it, fork it, improve it.

---


