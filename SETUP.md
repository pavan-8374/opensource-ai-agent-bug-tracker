# 🐛 AI Agent Bug Tracker — Setup Guide

A Streamlit bug tracker that stores tickets and screenshots directly in GitHub.

---

## 📁 Files in this project

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit web app |
| `tickets.json` | Ticket data (auto-updated by the app) |
| `requirements.txt` | Python dependencies |
| `secrets.toml.example` | Template for your secrets |

---

## 🚀 Setup Steps (takes ~10 minutes)

### Step 1 — Create a GitHub Repo

1. Go to [github.com/new](https://github.com/new)
2. Name it `ai-agent-bug-tracker`
3. Set it to **Private**
4. Click **Create repository**
5. Upload all 3 files: `app.py`, `tickets.json`, `requirements.txt`

---

### Step 2 — Create a GitHub Personal Access Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name: `bug-tracker`
4. Set expiration: **No expiration** (or 1 year)
5. Check the **`repo`** scope (full control of private repositories)
6. Click **Generate token**
7. **Copy the token** — you won't see it again!

---

### Step 3 — Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Select your repo: `ai-agent-bug-tracker`
5. Branch: `main`
6. Main file: `app.py`
7. Click **Deploy**

---

### Step 4 — Add Your Secrets

1. Once deployed, click **⋮ (three dots)** → **Settings** → **Secrets**
2. Paste this (with your real values):

```toml
GITHUB_TOKEN = "ghp_your_token_here"
GITHUB_REPO  = "your-username/ai-agent-bug-tracker"
```

3. Click **Save** — the app will restart automatically

---

### Step 5 — Share with Your Developer

- Just send them the Streamlit URL (e.g. `https://your-app.streamlit.app`)
- They can view all tickets, screenshots, and update statuses
- No login needed (unless you enable Streamlit auth)

---

## ✅ You're live!

Your bug tracker will:
- Store all tickets in `tickets.json` in your GitHub repo
- Store screenshots in the `/screenshots` folder in your repo
- Update in real time as you log new bugs
