"""Job Search Ledger: a personal job application tracker."""
import hashlib
import json
import os
import re
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

from themes import DEFAULT, THEMES

HERE = Path(__file__).parent


def _settings():
    """Settings come from env vars, then settings.json (git ignored), then defaults."""
    cfg = {}
    f = Path(os.environ.get("JOB_TRACKER_SETTINGS", HERE / "settings.json"))
    if f.exists():
        cfg = json.loads(f.read_text(encoding="utf-8"))
    env = {k: os.environ.get("JOB_TRACKER_" + k.upper()) for k in ["csv", "db", "target", "name", "theme"]}
    cfg.update({k: v for k, v in env.items() if v})
    return cfg


CFG = _settings()
DEFAULT_CSV = HERE / "data" / "job_applications.csv"  # used by "Start from scratch" (git ignored)
COLUMNS = ["Date Applied", "Company", "Position", "Status", "Pay Listed", "Location/Remote", "Source",
           "Apply Method/ATS", "Confirmation", "URL", "Notes", "Evidence"]
CSV_CONFIGURED = bool(CFG.get("csv"))
CSV_PATH = Path(os.path.expandvars(os.path.expanduser(str(CFG.get("csv") or DEFAULT_CSV))))
if not CSV_PATH.is_absolute():
    CSV_PATH = HERE / CSV_PATH
DB_PATH = Path(os.path.expandvars(os.path.expanduser(str(CFG.get("db") or HERE / "data" / "tracker.db"))))
TARGET = int(CFG.get("target") or 90000)
APPLICANT = CFG.get("name") or "Your Name"
FIRST = APPLICANT.split()[0] if CFG.get("name") else "You"
NEEDS = f"Needs {FIRST}"  # any CSV status starting with "Needs" maps here



# ---------- theme (saved in SQLite between runs) ----------
def _pref(key, value=None):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute("CREATE TABLE IF NOT EXISTS prefs (key TEXT PRIMARY KEY, value TEXT)")
        if value is not None:
            con.execute("INSERT INTO prefs VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        row = con.execute("SELECT value FROM prefs WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def _pick_theme():
    for name in (st.query_params.get("theme"), _pref("theme"), CFG.get("theme")):
        if name in THEMES:
            return name
    return DEFAULT


THEME = _pick_theme()
T = THEMES[THEME]
_native = {"base": T["base"], "primaryColor": T["accent"], "backgroundColor": T["bg"],
           "secondaryBackgroundColor": T["panel"], "textColor": T["ink"]}
_THEME_CHANGED = any(st._config.get_option(f"theme.{k}") != v for k, v in _native.items())
for _k, _v in _native.items():  # Streamlit's own widgets read this when the page loads
    st._config.set_option(f"theme.{_k}", _v)
PAPER, PANEL, INK, MUTED, RULE = T["bg"], T["panel"], T["ink"], T["muted"], T["rule"]
ACCENT, ACCENT2 = T["accent"], T["accent2"]

STATUSES = ["Applied", "Viewed", "Interviewing", "Interviewed", "Offer", "Rejected",
            NEEDS, "Skipped", "Already Applied", "Closed-Filled"]
NOT_SUBMITTED = {NEEDS, "Skipped", "Already Applied"}
INTERVIEW = {"Interviewing", "Interviewed"}
RESPONDED = {"Viewed", "Interviewing", "Interviewed", "Offer", "Rejected"}

st.set_page_config(page_title="Job Search Ledger", layout="wide")

# ---------- styling (all values come from the theme dict) ----------
with st.sidebar:
    _choice = st.selectbox("Theme", list(THEMES), index=list(THEMES).index(THEME), help="Saved for next time")
    if _choice != THEME:
        _pref("theme", _choice)
        st.query_params.clear()
        _THEME_CHANGED = True
    if st.button("Refresh data", help="Reload the tracker CSV now", width="stretch"):
        st.cache_data.clear()
        st.rerun()


@st.fragment(run_every=30)
def _watch_csv():
    """Rerun the app when the tracker CSV changes on disk (e.g. OneDrive sync)."""
    try:
        m = CSV_PATH.stat().st_mtime
    except OSError:
        return
    last = st.session_state.get("_csv_mtime")
    st.session_state["_csv_mtime"] = m
    if last is not None and m != last:
        st.rerun(scope="app")


with st.sidebar:
    _watch_csv()
if _THEME_CHANGED:  # reload once so tables and inputs pick up the new theme too
    st.html("<script>window.location.reload()</script>", unsafe_allow_javascript=True)
    st.stop()

st.markdown(f"""
<style>
@import url('{T["font_url"]}');
html, body, .stApp, .stMarkdown, p, label, input, textarea, button {{ font-family: '{T["body"]}', sans-serif; }}
.stApp {{ background: {PAPER}; color: {INK}; }}
.block-container {{ padding-top: 2.2rem; max-width: 1320px; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.mast {{ display:flex; justify-content:space-between; align-items:center; gap:18px; padding-bottom: 14px; position:relative; }}
.mast:after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:2px; background: {T["header_rule"]}; }}
.brand {{ display:flex; align-items:center; gap:16px; }}
.emblem {{ width:44px; height:44px; flex:none; {T["emblem"]} }}
.mast h1 {{ font-family:'{T["display"]}', sans-serif; font-weight:400; font-size:2rem; margin:0; padding:0; letter-spacing:.03em;
  color:{INK}; text-shadow: {T["title_glow"]}; }}
.mast h1 em {{ font-style:normal; color:{ACCENT}; }}
.mast .meta {{ color:{MUTED}; font-size:.78rem; text-align:right; line-height:1.6; font-family:'{T["mono"]}', monospace; }}
.mast .meta b {{ color:{ACCENT2}; font-weight:500; }}
.stats {{ display:grid; grid-template-columns: repeat(5, 1fr); gap:12px; margin: 1.3rem 0 1.4rem; }}
.stat {{ background:{PANEL}; border:1px solid {RULE}; border-radius:{T["radius"]}; padding: 14px 16px; }}
.stat .lbl {{ color:{MUTED}; font-size:.7rem; text-transform:uppercase; letter-spacing:.14em; font-family:'{T["mono"]}', monospace; }}
.stat .val {{ font-family:'{T["mono"]}', monospace; font-size:2rem; font-weight:500; color:{INK}; margin-top:4px; }}
.stat.key {{ border-color:{ACCENT}; box-shadow:{T["key_glow"]}; }}
.stat.key .val {{ color:{ACCENT}; text-shadow:{T["title_glow"].replace("18px", "14px")}; }}
.stat .hint {{ color:{MUTED}; font-size:.75rem; }}
.sec {{ font-family:'{T["mono"]}', monospace; font-size:.74rem; text-transform:uppercase; letter-spacing:.16em; color:{ACCENT2};
  border-bottom:1px solid {RULE}; padding-bottom:6px; margin:.6rem 0 .6rem; }}
.sec:before {{ content:"{T["sec_prefix"]}"; color:{ACCENT}; white-space:pre; }}
.note {{ color:{MUTED}; font-size:.82rem; }}
.note b {{ color:{INK}; font-weight:500; font-family:'{T["mono"]}', monospace; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 26px; border-bottom:1px solid {RULE}; }}
.stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"] p {{ padding: 6px 0; color:{MUTED}; }}
section[data-testid="stSidebar"] {{ background:{PANEL}; border-right:1px solid {RULE}; }}
section[data-testid="stSidebar"] * {{ color:{INK}; }}
.stTabs [data-baseweb="tab"] p {{ font-family:'{T["mono"]}', monospace; font-size:.85rem; letter-spacing:.06em; text-transform:uppercase; }}
.stTabs [aria-selected="true"], .stTabs [aria-selected="true"] p {{ color:{INK}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background:{ACCENT}; }}
.item {{ border-top:1px solid {RULE}; padding:11px 0; display:grid; grid-template-columns: 1fr 2fr auto; gap:16px; font-size:.9rem; }}
.item .m {{ color:{MUTED}; font-size:.8rem; }}
.item a, .item a:visited {{ color:{ACCENT2}; text-decoration:none; font-family:'{T["mono"]}', monospace; font-size:.8rem; }}
.wk {{ border-top:1px solid {RULE}; padding:10px 0 2px; display:flex; justify-content:space-between; gap:12px; font-size:.9rem; white-space:nowrap; }}
.wk b {{ font-weight:500; }}
.wk .n {{ font-family:'{T["mono"]}', monospace; color:{MUTED}; font-size:.8rem; }}
.ok {{ color:{ACCENT2}; }} .pending {{ color:{ACCENT}; }}
.foot {{ margin-top:2.5rem; color:{MUTED}; opacity:.6; font-family:'{T["mono"]}', monospace; font-size:.7rem; letter-spacing:.12em; text-align:center; }}
{T["extra_css"]}
</style>""", unsafe_allow_html=True)

# ---------- storage ----------
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS edits (key TEXT PRIMARY KEY, status TEXT, notes TEXT, contact TEXT, updated TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS weeks (week_end TEXT PRIMARY KEY, reported INTEGER, reported_on TEXT)")
    return con


def row_key(r):
    raw = "|".join(str(r.get(c, "")) for c in ["Date Applied", "Company", "Position", "URL"])
    return hashlib.sha1(raw.lower().encode()).hexdigest()[:16]


def parse_pay(s):
    """Return (low, high) annualized dollars or (None, None)."""
    if not isinstance(s, str):
        return None, None
    t = s.replace(",", "").lower()
    nums = []
    for m in re.finditer(r"\$?\s*(\d+(?:\.\d+)?)\s*(k)?", t):
        v = float(m.group(1))
        if m.group(2):
            v *= 1000
        nums.append(v)
    nums = [n for n in nums if n >= 10][:2]
    if not nums:
        return None, None
    if "/hr" in t or "hour" in t or max(nums) < 400:
        nums = [n * 2080 for n in nums]
    return min(nums), max(nums)


@st.cache_data(ttl=60)
def load_csv(path, mtime):
    df = pd.read_csv(path, dtype=str).fillna("")
    for c in COLUMNS:  # minimal CSVs work: missing columns are just blank
        if c not in df.columns:
            df[c] = ""
    df = df[df["Company"].str.strip() != ""].copy()
    df["Status"] = df["Status"].where(df["Status"].str.strip() != "", "Applied")
    df["date"] = pd.to_datetime(df["Date Applied"], errors="coerce")
    df["key"] = [row_key(r) for _, r in df.iterrows()]
    return df


def load():
    df = load_csv(str(CSV_PATH), CSV_PATH.stat().st_mtime)
    edits = pd.read_sql("SELECT key, status AS e_status, notes AS e_notes, contact AS e_contact FROM edits", db())
    df = df.merge(edits, on="key", how="left")
    df["Status"] = df["e_status"].where(df["e_status"].notna() & (df["e_status"] != ""), df["Status"])
    df["Status"] = df["Status"].str.replace(r"^Needs\b.*$", NEEDS, regex=True)
    df["My Notes"] = df["e_notes"].fillna("")
    df["Contact"] = df["e_contact"].fillna("")
    pay = df["Pay Listed"].apply(parse_pay)
    df["pay_lo"] = [p[0] for p in pay]
    df["pay_hi"] = [p[1] for p in pay]
    df["week_end"] = df["date"].apply(lambda d: (d + timedelta(days=(5 - d.weekday()) % 7)).date() if pd.notna(d) else None)
    return df


def save_edit(key, status, notes, contact):
    con = db()
    con.execute("INSERT INTO edits VALUES (?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET status=excluded.status, "
                "notes=excluded.notes, contact=excluded.contact, updated=excluded.updated",
                (key, status, notes, contact, datetime.now().isoformat(timespec="seconds")))
    con.commit()


def weeks_reported():
    return {r[0]: bool(r[1]) for r in db().execute("SELECT week_end, reported FROM weeks")}


def set_week(week_end, val):
    con = db()
    con.execute("INSERT INTO weeks VALUES (?,?,?) ON CONFLICT(week_end) DO UPDATE SET reported=excluded.reported, reported_on=excluded.reported_on",
                (str(week_end), int(val), date.today().isoformat() if val else None))
    con.commit()


def plot_base(fig, h=320):
    fig.update_layout(template="plotly_dark" if T["base"] == "dark" else "plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=h, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
                      font=dict(family=f"{T['body']}, sans-serif", color=INK, size=12))
    for ax in (fig.update_xaxes, fig.update_yaxes):
        ax(linecolor=RULE, gridcolor=RULE, zeroline=False, tickfont=dict(color=INK))
    return fig


# ---------- welcome (no CSV yet) ----------
def _csv_ready():
    try:
        return CSV_PATH.read_text(encoding="utf-8-sig").strip() != ""
    except OSError:
        return False


if not _csv_ready():
    st.markdown('<div class="mast"><div class="brand"><div class="emblem"></div><h1>Welcome to Job Search <em>Ledger</em></h1></div></div>',
                unsafe_allow_html=True)
    st.write("")
    if CSV_CONFIGURED:
        st.caption(f"The tracker CSV in your settings is missing or empty: {CSV_PATH}")
    else:
        st.caption("No tracker CSV is set up yet. Pick one of these to get going.")
    w1, w2 = st.columns(2, gap="large")
    with w1:
        st.markdown('<div class="sec">Import my spreadsheet</div>', unsafe_allow_html=True)
        st.markdown("1. In Excel or Google Sheets, save or download your tracker as **CSV**.\n"
                    "2. Only **Date Applied**, **Company** and **Position** are needed. Other columns are optional, "
                    "and extra columns are fine.\n"
                    f"3. Upload it below. It is saved to `{CSV_PATH}`.")
        up = st.file_uploader("Your tracker CSV", type=["csv"])
        if up is not None and st.button("Import", type="primary"):
            try:
                cols = pd.read_csv(up, dtype=str, nrows=0).columns
            except Exception as e:  # noqa: BLE001
                st.error(f"That file could not be read as a CSV: {e}")
            else:
                if "Company" not in cols:
                    st.error("The file needs at least a Company column (plus Date Applied and Position).")
                else:
                    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
                    CSV_PATH.write_bytes(up.getvalue())
                    st.cache_data.clear(); st.rerun()
    with w2:
        st.markdown('<div class="sec">Start from scratch</div>', unsafe_allow_html=True)
        st.markdown(f"Creates a blank tracker with all the columns the ledger uses at `{CSV_PATH}`. "
                    "Then add applications from the sidebar as you go.")
        if st.button("Start from scratch", type="primary"):
            CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)
            st.cache_data.clear(); st.rerun()
        st.caption("Just looking? Set JOB_TRACKER_CSV=sample_data.csv to explore the fake sample data.")
    st.stop()


# ---------- add / edit ----------
def append_row(values):
    """Append one application to the tracker CSV, adding any missing standard columns."""
    cur = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
    for c in COLUMNS:
        if c not in cur.columns:
            cur[c] = ""
    row = {c: values.get(c, "") for c in cur.columns}
    pd.concat([cur, pd.DataFrame([row])], ignore_index=True).to_csv(CSV_PATH, index=False)
    st.cache_data.clear()


with st.sidebar:
    with st.expander("Add application", expanded=False):
        with st.form("add_app", clear_on_submit=True):
            company = st.text_input("Company *", key="add_company")
            position = st.text_input("Position *", key="add_position")
            applied = st.date_input("Date applied *", value=date.today())
            url = st.text_input("Job URL")
            p1, p2 = st.columns(2)
            pmin = p1.number_input("Pay min ($)", min_value=0, value=None, step=1000)
            pmax = p2.number_input("Pay max ($)", min_value=0, value=None, step=1000, key="add_pmax")
            loc = st.text_input("Location / remote")
            source = st.text_input("Source", placeholder="LinkedIn, Indeed, referral")
            status = st.selectbox("Status", STATUSES, index=0)
            notes = st.text_area("Notes")
            if st.form_submit_button("Add", type="primary", width="stretch"):
                if not company.strip() or not position.strip():
                    st.error("Company and Position are required.")
                else:
                    pays = [f"${int(x):,}" for x in (pmin, pmax) if x]
                    append_row({"Date Applied": applied.isoformat(), "Company": company.strip(), "Position": position.strip(),
                                "Status": status, "Pay Listed": "-".join(pays), "Location/Remote": loc.strip(),
                                "Source": source.strip(), "URL": url.strip(), "Notes": notes.strip()})
                    st.session_state["_toast"] = f"Added {company.strip()}"
                    st.rerun()
    if st.session_state.get("_toast"):
        st.toast(st.session_state.pop("_toast"))


# ---------- data ----------
df = load()
sub = df[~df["Status"].isin(NOT_SUBMITTED)]
today = pd.Timestamp(date.today())
wk_start = today - timedelta(days=(today.weekday() + 1) % 7)  # Sunday
this_week = sub[sub["date"] >= wk_start]
interviews = df[df["Status"].isin(INTERVIEW | {"Offer"})]
needs = df[df["Status"] == NEEDS]
resp_rate = (sub["Status"].isin(RESPONDED).sum() / len(sub) * 100) if len(sub) else 0

with st.sidebar:
    if len(df):
        with st.expander("Edit status", expanded=False):
            opts = df.sort_values("date", ascending=False).drop_duplicates("key").set_index("key")
            pick = st.selectbox("Application", opts.index, format_func=lambda k: " / ".join(
                x for x in opts.loc[k, ["Company", "Position", "Date Applied"]] if x))
            r = opts.loc[pick]
            new = st.selectbox("New status", STATUSES, index=STATUSES.index(r["Status"]) if r["Status"] in STATUSES else 0)
            if st.button("Save status", width="stretch"):
                save_edit(pick, new, r["My Notes"], r["Contact"])
                st.session_state["_toast"] = f"{r['Company']} is now {new}"
                st.rerun()

# ---------- header ----------
upd = datetime.fromtimestamp(CSV_PATH.stat().st_mtime).strftime("%b %d, %Y %I:%M %p")
st.markdown(f'<div class="mast"><div class="brand"><div class="emblem"></div><h1>Job Search <em>Ledger</em></h1></div>'
            f'<div class="meta">{APPLICANT}<br>source <b>{CSV_PATH.name}</b><br>synced {upd}</div></div>', unsafe_allow_html=True)
stats = [("Total applied", len(sub), f"of {len(df)} roles tracked", ""),
         ("This week", len(this_week), f"since {wk_start:%a %b %d}", ""),
         ("Interviews", len(interviews), "in progress, done or offer", ""),
         (f"Needs {FIRST}", len(needs), "waiting on a manual step", "key"),
         ("Response rate", f"{resp_rate:.1f}%", "any employer response", "")]
st.markdown('<div class="stats">' + "".join(
    f'<div class="stat {c}"><div class="lbl">{l}</div><div class="val">{v}</div><div class="hint">{h}</div></div>'
    for l, v, h, c in stats) + '</div>', unsafe_allow_html=True)

tabs = st.tabs(["Overview", "Applications", f"Needs {FIRST}", "Weekly report"])

# ---------- overview ----------
with tabs[0]:
    a, b = st.columns([1, 1.6])
    with a:
        st.markdown('<div class="sec">Pipeline</div>', unsafe_allow_html=True)
        n_off = (sub["Status"] == "Offer").sum()
        n_int = sub["Status"].isin(INTERVIEW).sum() + n_off
        n_view = sub["Status"].isin({"Viewed", "Rejected"}).sum() + n_int
        fig = go.Figure(go.Funnel(y=["Applied", "Viewed", "Interview", "Offer"], x=[len(sub), n_view, n_int, n_off],
                                  textinfo="value+percent initial", textposition=["inside", "outside", "outside", "outside"],
                                  textfont=dict(family=T["mono"], color=[T["on_accent2"], INK, INK, INK]),
                                  marker=dict(color=T["funnel"], line=dict(width=1, color=RULE)),
                                  connector=dict(fillcolor=PANEL, line=dict(width=0))))
        st.plotly_chart(plot_base(fig, 330), width="stretch")
    with b:
        st.markdown('<div class="sec">Applications per day</div>', unsafe_allow_html=True)
        counts = sub.dropna(subset=["date"]).groupby(sub["date"].dt.date).size()
        start = (min(counts.index) if len(counts) else today.date()) - timedelta(days=7)
        start -= timedelta(days=(start.weekday() + 1) % 7)
        days = pd.date_range(start, today, freq="D")
        z, txt, xs = [[None] * 0 for _ in range(7)], [[] for _ in range(7)], []
        for i in range(0, len(days), 7):
            wk = days[i:i + 7]
            xs.append(wk[0].strftime("%b %d"))
            for j in range(7):
                if j < len(wk):
                    v = int(counts.get(wk[j].date(), 0))
                    z[j].append(v)
                    txt[j].append(f"{wk[j]:%a %b %d}: {v} apps")
                else:
                    z[j].append(None); txt[j].append("")
        fig = go.Figure(go.Heatmap(z=z, x=xs, y=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], text=txt,
                                   hoverinfo="text", xgap=4, ygap=4,
                                   colorscale=[[0, T["heat"][0]], [0.01, T["heat"][1]], [0.5, T["heat"][2]], [1, T["heat"][3]]],
                                   colorbar=dict(thickness=8, outlinewidth=0, len=.8)))
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(showgrid=False, side="top")
        st.plotly_chart(plot_base(fig, 330), width="stretch")

    st.markdown(f'<div class="sec">Listed pay against ${TARGET//1000}K target</div>', unsafe_allow_html=True)
    pay = df.dropna(subset=["pay_lo"]).sort_values("pay_hi").copy()
    pay["pay_lo"], pay["pay_hi"] = pay["pay_lo"].astype(float), pay["pay_hi"].astype(float)
    pay["label"] = pay["Company"].str.slice(0, 22) + ", " + pay["Position"].str.slice(0, 26)
    hit = pay["pay_hi"] >= TARGET
    colors = [T["pay_hit"] if h else T["pay_miss"] for h in hit]
    hatch = ["" if h else "/" for h in hit]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=pay["pay_hi"] - pay["pay_lo"] + 1500, base=pay["pay_lo"] - 750, y=pay["label"], orientation="h",
                         marker=dict(color=colors, line=dict(width=0), pattern=dict(shape=hatch, fgcolor=PAPER, size=6, solidity=.25)), customdata=pay[["Pay Listed", "Status"]],
                         hovertemplate="%{y}<br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>"))
    fig.add_vline(x=TARGET, line=dict(color=ACCENT, width=1.5, dash="dot"),
                  annotation_text=f"${TARGET//1000}K target", annotation_font_color=ACCENT, annotation_position="top")
    fig.update_xaxes(tickprefix="$", tickformat="~s", gridcolor=RULE, showgrid=True)
    fig.update_yaxes(tickfont=dict(size=10))
    st.plotly_chart(plot_base(fig, max(320, 18 * len(pay))).update_layout(margin=dict(t=34)), width="stretch")
    above = (pay["pay_hi"] >= TARGET).sum()
    if not len(pay):
        st.markdown('<div class="note">No listed pay yet. Add a pay range to see roles here.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="note"><b>{len(pay)}</b> roles list pay. <b>{above}</b> reach the target. '
                    f'Median top of range <b>${pay["pay_hi"].median()/1000:.0f}K</b>. Hourly rates annualized at 2,080 hours; '
                    f'hatched bars top out below target.</div>', unsafe_allow_html=True)


# ---------- editable table ----------
EDIT_COLS = ["Date Applied", "Company", "Position", "Status", "Pay Listed", "Location/Remote", "Source", "URL", "My Notes", "Contact"]


def editor(frame, key):
    view = frame[EDIT_COLS + ["key"]].set_index("key")
    edited = st.data_editor(
        view, key=key, width="stretch", hide_index=True, height=min(640, 38 + 35 * len(view)), disabled=EDIT_COLS[:3] + EDIT_COLS[4:8],
        column_config={
            "Status": st.column_config.SelectboxColumn(options=STATUSES, required=True),
            "URL": st.column_config.LinkColumn("Link", display_text="Open"),
            "My Notes": st.column_config.TextColumn(width="large"),
            "Contact": st.column_config.TextColumn(help="Recruiter or contact for the work search log"),
        })
    changed = 0
    for k in edited.index:
        o, n = view.loc[k], edited.loc[k]
        if (o["Status"], o["My Notes"], o["Contact"]) != (n["Status"], n["My Notes"], n["Contact"]):
            save_edit(k, n["Status"], n["My Notes"], n["Contact"]); changed += 1
    if changed:
        st.toast(f"Saved {changed} edit(s)")
    return edited


with tabs[1]:
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1.2])
    q = f1.text_input("Search", placeholder="company, title, notes")
    stat = f2.multiselect("Status", STATUSES, default=[])
    src = f3.multiselect("Source", sorted(df["Source"].unique()))
    min_pay = f4.checkbox("At or above target pay")
    v = df.copy()
    if q:
        v = v[v[["Company", "Position", "Notes", "My Notes"]].apply(lambda r: q.lower() in " ".join(r).lower(), axis=1)]
    if stat:
        v = v[v["Status"].isin(stat)]
    if src:
        v = v[v["Source"].isin(src)]
    if min_pay:
        v = v[v["pay_hi"].fillna(0) >= TARGET]
    st.caption(f"{len(v)} of {len(df)} rows. Edit Status, My Notes and Contact inline; edits save to SQLite, the source CSV is never touched")
    editor(v.sort_values("date", ascending=False), "main")

with tabs[2]:
    if needs.empty:
        st.markdown('<div class="note">Nothing is waiting on you.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sec">{len(needs)} applications waiting on a manual step</div>', unsafe_allow_html=True)
        for _, r in needs.sort_values("date", ascending=False).head(8).iterrows():
            st.markdown(f'<div class="item"><div><b>{r["Company"]}</b><div class="m">{r["Date Applied"]}</div></div>'
                        f'<div>{r["Position"]}<div class="m">{r["Confirmation"] or r["Notes"]}, {r["Apply Method/ATS"] or r["Source"]}</div></div>'
                        f'<div><a href="{r["URL"]}" target="_blank">Open posting</a></div></div>', unsafe_allow_html=True)
        st.caption("Flip a row to Applied once you finish it.")
        editor(needs.sort_values("date", ascending=False), "needs")


# ---------- weekly report ----------
def report_frame(week_df):
    out = pd.DataFrame({
        "Date": week_df["date"].dt.strftime("%m/%d/%Y"),
        "Company": week_df["Company"],
        "Position": week_df["Position"],
        "Method": week_df.apply(lambda r: "Online: " + " / ".join(dict.fromkeys(x for x in [r["Source"], r["Apply Method/ATS"]] if x)), axis=1),
        "Contact": week_df.apply(lambda r: r["Contact"] or r["URL"], axis=1),
        "Result": week_df["Status"].replace({"Applied": "Pending"}),
    })
    return out.sort_values("Date")


def ascii_safe(s):
    return str(s).encode("latin-1", "replace").decode("latin-1")


def report_pdf(rep, week_end):
    start = week_end - timedelta(days=6)
    pdf = FPDF(orientation="L", unit="mm", format="Letter")
    pdf.set_auto_page_break(True, 12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, "Work Search Activity Log", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, ascii_safe(f"Name: {APPLICANT}    Week: {start:%m/%d/%Y} to {week_end:%m/%d/%Y} (Sun to Sat)    "
                              f"Contacts this week: {len(rep)}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    widths = [22, 52, 62, 50, 58, 22]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(20, 27, 38); pdf.set_text_color(255, 255, 255)
    for w, h in zip(widths, rep.columns):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln(); pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 8)
    for _, r in rep.iterrows():
        for w, val in zip(widths, r.values):
            s = ascii_safe(val)
            while pdf.get_string_width(s) > w - 2 and len(s) > 3:
                s = s[:-4] + "..."
            pdf.cell(w, 6, s, border=1)
        pdf.ln()
    return bytes(pdf.output())


with tabs[3]:
    rep_flags = weeks_reported()
    wk = sub.dropna(subset=["week_end"]).groupby("week_end")
    weeks = sorted(wk.groups.keys(), reverse=True)
    if not weeks:
        st.info("No dated applications yet.")
    left, right = st.columns([1.25, 2], gap="large")
    with left:
        st.markdown('<div class="sec">Weeks</div>', unsafe_allow_html=True)
        for we in weeks:
            g = wk.get_group(we)
            done = rep_flags.get(str(we), False)
            st.markdown(f'<div class="wk"><span><b>Week ending {we:%b %d}</b></span>'
                        f'<span class="n">{len(g)} apps, {g["Status"].isin(RESPONDED).sum()} resp, '
                        f'<span class="{"ok" if done else "pending"}">{"reported" if done else "not reported"}</span></span></div>',
                        unsafe_allow_html=True)
            nv = st.checkbox("Reported", value=done, key=f"wk{we}")
            if nv != done:
                set_week(we, nv); st.rerun()
    with right:
        if weeks:
            sel = st.selectbox("Report week (Sunday to Saturday)", weeks, format_func=lambda d: f"Week ending Sat {d:%b %d, %Y}")
            rep = report_frame(wk.get_group(sel))
            st.markdown(f'<div class="sec">Work search log, {len(rep)} contacts</div>', unsafe_allow_html=True)
            st.dataframe(rep, width="stretch", hide_index=True, height=min(520, 38 + 35 * len(rep)))
            d1, d2, _ = st.columns([1, 1, 2])
            d1.download_button("Download CSV", rep.to_csv(index=False).encode(), f"work_search_{sel}.csv", "text/csv", width="stretch")
            d2.download_button("Download PDF", report_pdf(rep, sel), f"work_search_{sel}.pdf", "application/pdf", width="stretch")
            st.caption("Add a recruiter name or email in the Contact column on the Applications tab; otherwise the posting link is used.")

st.markdown('<div class="foot">END OF LEDGER</div>', unsafe_allow_html=True)
