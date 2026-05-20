import streamlit as st
import json
import base64
import requests
from datetime import datetime
import random
import string

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bug Tracker · AI Agent",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0a0a0f;
        color: #e2e8f0;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #f1f5f9 !important;
    }
    .ticket-card {
        background: #0f1117;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .ticket-card:hover {
        border-color: #334155;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-family: 'DM Mono', monospace;
        font-weight: 500;
        margin-right: 6px;
    }
    .sev-low    { background: #6b728022; color: #9ca3af; border: 1px solid #6b728044; }
    .sev-medium { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
    .sev-high   { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
    .sev-critical{ background: #dc262622; color: #dc2626; border: 1px solid #dc262644; }
    .status-open      { background: #ef444415; color: #ef4444; border: 1px solid #ef444433; }
    .status-progress  { background: #f59e0b15; color: #f59e0b; border: 1px solid #f59e0b33; }
    .status-fixed     { background: #3b82f615; color: #3b82f6; border: 1px solid #3b82f633; }
    .status-verified  { background: #22c55e15; color: #22c55e; border: 1px solid #22c55e33; }
    .ticket-id {
        font-family: 'DM Mono', monospace;
        color: #475569;
        font-size: 12px;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #0f1117 !important;
        color: #e2e8f0 !important;
        border-color: #1e293b !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover {
        opacity: 0.9;
        border: none;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f1117;
        border-right: 1px solid #1e293b;
    }
    .metric-card {
        background: #0f1117;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-number {
        font-size: 32px;
        font-weight: 700;
        font-family: 'DM Mono', monospace;
    }
    .metric-label {
        font-size: 11px;
        color: #475569;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-top: 4px;
    }
    hr {
        border-color: #1e293b !important;
    }
    .screenshot-box {
        border: 1px solid #1e293b;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── GitHub helpers ────────────────────────────────────────────────────────────
def get_github_config():
    token = st.secrets.get("GITHUB_TOKEN", "")
    repo  = st.secrets.get("GITHUB_REPO", "")   # e.g. "username/ai-agent-bug-tracker"
    return token, repo

def github_headers():
    token, _ = get_github_config()
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

def load_tickets():
    _, repo = get_github_config()
    url = f"https://api.github.com/repos/{repo}/contents/tickets.json"
    r = requests.get(url, headers=github_headers())
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        tickets = json.loads(content)
        return tickets, data["sha"]
    return [], None

def save_tickets(tickets, sha=None):
    _, repo = get_github_config()
    url = f"https://api.github.com/repos/{repo}/contents/tickets.json"
    content = base64.b64encode(json.dumps(tickets, indent=2).encode()).decode()
    payload = {
        "message": f"Update tickets [{datetime.now().strftime('%Y-%m-%d %H:%M')}]",
        "content": content,
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=github_headers(), json=payload)
    return r.status_code in (200, 201)

def upload_screenshot(file_bytes, filename, ticket_id):
    _, repo = get_github_config()
    path = f"screenshots/{ticket_id}_{filename}"
    url  = f"https://api.github.com/repos/{repo}/contents/{path}"
    # Check if exists
    existing = requests.get(url, headers=github_headers())
    payload = {
        "message": f"Add screenshot for {ticket_id}",
        "content": base64.b64encode(file_bytes).decode(),
    }
    if existing.status_code == 200:
        payload["sha"] = existing.json()["sha"]
    r = requests.put(url, headers=github_headers(), json=payload)
    if r.status_code in (200, 201):
        _, repo_name = get_github_config()
        raw_url = f"https://raw.githubusercontent.com/{repo_name}/main/{path}"
        return raw_url
    return None

def generate_id():
    return "TCK-" + "".join(random.choices(string.digits, k=4))

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐛 Bug Tracker")
    st.markdown("<small style='color:#475569'>opensource-ai-agent.uk/app</small>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", ["📋 All Tickets", "➕ New Ticket", "📊 Dashboard"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<small style='color:#334155'>Data stored on GitHub<br>Hosted on Streamlit Cloud</small>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def cached_load():
    return load_tickets()

tickets, sha = cached_load()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL TICKETS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📋 All Tickets":
    st.markdown("## 📋 All Tickets")

    if not tickets:
        st.info("No tickets yet. Create your first one from **➕ New Ticket**.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            f_status = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Fixed", "Verified"])
        with col2:
            f_sev = st.selectbox("Filter by Severity", ["All", "Critical", "High", "Medium", "Low"])
        with col3:
            f_type = st.selectbox("Filter by Type", ["All", "Functional", "UI", "Both"])

        filtered = tickets
        if f_status != "All":
            filtered = [t for t in filtered if t.get("status") == f_status]
        if f_sev != "All":
            filtered = [t for t in filtered if t.get("severity") == f_sev]
        if f_type != "All":
            filtered = [t for t in filtered if t.get("testType") == f_type]

        st.markdown(f"<small style='color:#475569'>Showing {len(filtered)} ticket(s)</small>", unsafe_allow_html=True)
        st.markdown("")

        sev_class = {"Low": "sev-low", "Medium": "sev-medium", "High": "sev-high", "Critical": "sev-critical"}
        sta_class  = {"Open": "status-open", "In Progress": "status-progress", "Fixed": "status-fixed", "Verified": "status-verified"}

        for t in filtered:
            with st.expander(f"**{t['id']}** — {t['title']}", expanded=False):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(
                        f"<span class='badge {sev_class.get(t['severity'], '')}'>{t['severity']}</span>"
                        f"<span class='badge {sta_class.get(t['status'], '')}'>{t['status']}</span>"
                        f"<span class='badge' style='background:#6366f115;color:#818cf8;border:1px solid #6366f133'>{t['testType']}</span>"
                        f"<span class='badge' style='background:#1e293b;color:#64748b'>{t.get('browser','')}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"<small class='ticket-id'>📅 {t['date']} · 🌐 {t.get('url','')}</small>", unsafe_allow_html=True)

                with c2:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Open", "In Progress", "Fixed", "Verified"],
                        index=["Open", "In Progress", "Fixed", "Verified"].index(t["status"]),
                        key=f"status_{t['id']}"
                    )
                    if new_status != t["status"]:
                        t["status"] = new_status
                        _, current_sha = load_tickets()
                        if save_tickets(tickets, current_sha):
                            st.cache_data.clear()
                            st.success("Status updated!")
                            st.rerun()

                st.markdown("---")
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown("**📋 Steps to Reproduce**")
                    st.markdown(f"<div style='background:#0a0a0f;padding:12px;border-radius:8px;border:1px solid #1e293b;white-space:pre-wrap;font-size:13px'>{t.get('steps','—')}</div>", unsafe_allow_html=True)
                with r2:
                    st.markdown("**✅ Expected**")
                    st.markdown(f"<div style='background:#0a0a0f;padding:12px;border-radius:8px;border:1px solid #1e293b;font-size:13px'>{t.get('expected','—')}</div>", unsafe_allow_html=True)
                    st.markdown("**❌ Actual**")
                    st.markdown(f"<div style='background:#0a0a0f;padding:12px;border-radius:8px;border:1px solid #1e293b;font-size:13px'>{t.get('actual','—')}</div>", unsafe_allow_html=True)

                if t.get("notes"):
                    st.markdown("**📝 Notes**")
                    st.markdown(f"<div style='background:#0a0a0f;padding:12px;border-radius:8px;border:1px solid #1e293b;font-size:13px'>{t['notes']}</div>", unsafe_allow_html=True)

                if t.get("screenshot_url"):
                    st.markdown("**📸 Screenshot**")
                    st.image(t["screenshot_url"], use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: NEW TICKET
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ New Ticket":
    st.markdown("## ➕ New Bug Ticket")
    st.markdown("<small style='color:#475569'>Fill in the details below. All fields except Notes are required.</small>", unsafe_allow_html=True)
    st.markdown("")

    with st.form("new_ticket_form", clear_on_submit=True):
        title = st.text_input("🐛 Bug Title *", placeholder="Short, clear description of the issue")

        c1, c2, c3 = st.columns(3)
        with c1:
            test_type = st.selectbox("Test Type *", ["Functional", "UI", "Both"])
        with c2:
            severity = st.selectbox("Severity *", ["Low", "Medium", "High", "Critical"])
        with c3:
            browser = st.selectbox("Browser *", ["Chrome", "Firefox", "Safari", "Edge", "Other"])

        steps = st.text_area("📋 Steps to Reproduce *", placeholder="1. Open the app\n2. Type a message\n3. Click Send", height=120)

        c4, c5 = st.columns(2)
        with c4:
            expected = st.text_area("✅ Expected Result *", placeholder="What should have happened", height=100)
        with c5:
            actual = st.text_area("❌ Actual Result *", placeholder="What actually happened", height=100)

        notes = st.text_area("📝 Notes (optional)", placeholder="Frequency, workaround, extra context...", height=80)

        screenshot = st.file_uploader("📸 Screenshot (optional)", type=["png", "jpg", "jpeg", "gif", "webp"])
        if screenshot:
            st.image(screenshot, caption="Preview", use_container_width=True)

        submitted = st.form_submit_button("🚀 Log Ticket", use_container_width=True)

        if submitted:
            if not title or not steps or not expected or not actual:
                st.error("Please fill in all required fields.")
            else:
                ticket_id = generate_id()
                screenshot_url = None

                if screenshot:
                    with st.spinner("Uploading screenshot to GitHub..."):
                        screenshot_url = upload_screenshot(
                            screenshot.read(),
                            screenshot.name,
                            ticket_id
                        )

                new_ticket = {
                    "id": ticket_id,
                    "title": title,
                    "testType": test_type,
                    "severity": severity,
                    "browser": browser,
                    "steps": steps,
                    "expected": expected,
                    "actual": actual,
                    "notes": notes,
                    "screenshot_url": screenshot_url,
                    "status": "Open",
                    "date": datetime.now().strftime("%d %b %Y %H:%M"),
                    "url": "https://opensource-ai-agent.uk/app",
                }

                with st.spinner("Saving ticket to GitHub..."):
                    _, current_sha = load_tickets()
                    all_tickets = tickets + [new_ticket] if tickets else [new_ticket]
                    # Put new ticket at top
                    all_tickets = [new_ticket] + [t for t in tickets]
                    success = save_tickets(all_tickets, current_sha)

                if success:
                    st.cache_data.clear()
                    st.success(f"✅ Ticket **{ticket_id}** logged successfully!")
                    st.balloons()
                else:
                    st.error("Failed to save ticket. Check your GitHub token and repo settings.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")

    if not tickets:
        st.info("No tickets yet to show stats.")
    else:
        total     = len(tickets)
        open_t    = len([t for t in tickets if t["status"] == "Open"])
        progress  = len([t for t in tickets if t["status"] == "In Progress"])
        fixed     = len([t for t in tickets if t["status"] == "Fixed"])
        verified  = len([t for t in tickets if t["status"] == "Verified"])
        critical  = len([t for t in tickets if t["severity"] == "Critical"])
        high      = len([t for t in tickets if t["severity"] == "High"])

        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            (c1, str(total),    "#f1f5f9", "TOTAL"),
            (c2, str(open_t),   "#ef4444", "OPEN"),
            (c3, str(fixed),    "#3b82f6", "FIXED"),
            (c4, str(verified), "#22c55e", "VERIFIED"),
        ]
        for col, num, color, label in metrics:
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-number' style='color:{color}'>{num}</div>
                    <div class='metric-label'>{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("")
        c5, c6 = st.columns(2)

        with c5:
            st.markdown("**By Severity**")
            for sev, count, color in [
                ("Critical", critical, "#dc2626"),
                ("High", high, "#ef4444"),
                ("Medium", len([t for t in tickets if t["severity"] == "Medium"]), "#f59e0b"),
                ("Low", len([t for t in tickets if t["severity"] == "Low"]), "#6b7280"),
            ]:
                pct = int(count / total * 100) if total else 0
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px'>
                    <div style='width:80px;font-size:12px;color:#94a3b8'>{sev}</div>
                    <div style='flex:1;background:#1e293b;border-radius:4px;height:8px'>
                        <div style='width:{pct}%;background:{color};height:8px;border-radius:4px'></div>
                    </div>
                    <div style='width:30px;font-size:12px;color:#64748b;font-family:DM Mono,monospace'>{count}</div>
                </div>""", unsafe_allow_html=True)

        with c6:
            st.markdown("**By Status**")
            for sta, count, color in [
                ("Open", open_t, "#ef4444"),
                ("In Progress", progress, "#f59e0b"),
                ("Fixed", fixed, "#3b82f6"),
                ("Verified", verified, "#22c55e"),
            ]:
                pct = int(count / total * 100) if total else 0
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px'>
                    <div style='width:80px;font-size:12px;color:#94a3b8'>{sta}</div>
                    <div style='flex:1;background:#1e293b;border-radius:4px;height:8px'>
                        <div style='width:{pct}%;background:{color};height:8px;border-radius:4px'></div>
                    </div>
                    <div style='width:30px;font-size:12px;color:#64748b;font-family:DM Mono,monospace'>{count}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Recent Tickets**")
        for t in tickets[:5]:
            sev_colors = {"Low":"#6b7280","Medium":"#f59e0b","High":"#ef4444","Critical":"#dc2626"}
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#0f1117;border:1px solid #1e293b;
                        border-radius:8px;margin-bottom:8px'>
                <div>
                    <span style='font-family:DM Mono,monospace;color:#475569;font-size:11px'>{t['id']}</span>
                    <span style='margin-left:12px;font-size:13px;color:#e2e8f0'>{t['title']}</span>
                </div>
                <span style='color:{sev_colors.get(t["severity"],"#fff")};font-size:11px'>{t["severity"]}</span>
            </div>""", unsafe_allow_html=True)
