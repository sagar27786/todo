import os
import json
import uuid
from datetime import datetime
import streamlit as st

# Team ToDo app for Santosh, Vishal, and Sagar
# Persists tasks, comments, and status across runs using a JSON file

PEOPLE = ["santosh", "vishal", "sagar"]
LABELS = {"santosh": "Santosh", "vishal": "Vishal", "sagar": "Sagar"}
DATA_FILE = os.path.join(os.path.dirname(__file__), "todo_data.json")

st.set_page_config(
    page_title="Team ToDo • Santosh • Vishal • Sagar",
    page_icon="✅",
    layout="wide",
)

# ---------------------- Persistence helpers ----------------------

def _default_data():
    return {p: {"tasks": []} for p in PEOPLE}


def load_data():
    if not os.path.exists(DATA_FILE):
        data = _default_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = _default_data()
    # ensure all people exist
    for p in PEOPLE:
        data.setdefault(p, {"tasks": []})
    return data


def save_data(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, DATA_FILE)


# ---------------------- Task operations ----------------------

def add_task(data, person, title, comment=None):
    task = {
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "comments": [],
    }
    if comment and comment.strip():
        task["comments"].append({
            "text": comment.strip(),
            "ts": datetime.utcnow().isoformat(timespec="seconds"),
        })
    data[person]["tasks"].append(task)
    save_data(data)


def remove_task(data, person, task_id):
    tasks = data[person]["tasks"]
    data[person]["tasks"] = [t for t in tasks if t["id"] != task_id]
    save_data(data)


def set_status(data, person, task_id, status):
    for t in data[person]["tasks"]:
        if t["id"] == task_id:
            t["status"] = status
            break
    save_data(data)


def add_comment(data, person, task_id, text):
    for t in data[person]["tasks"]:
        if t["id"] == task_id:
            t["comments"].append({
                "text": text.strip(),
                "ts": datetime.utcnow().isoformat(timespec="seconds"),
            })
            break
    save_data(data)


def counts(tasks):
    done = sum(1 for t in tasks if t.get("status") == "done")
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    total = len(tasks)
    return done, pending, total


# ---------------------- UI Helpers ----------------------

def inject_styles(dark_mode: bool):
    if dark_mode:
        palette = {
            "bg": "#0F172A",
            "card": "#111827",
            "text": "#F9FAFB",
            "muted": "#9CA3AF",
            "primary": "#60A5FA",
            "accent": "#34D399",
            "border": "#1F2937",
            "shadow": "0 6px 16px rgba(0,0,0,0.25)",
            "done_bg": "rgba(52, 211, 153, 0.10)",
            "pending_bg": "rgba(245, 158, 11, 0.10)",
            "sidebar_bg": "#0B1220",
        }
    else:
        palette = {
            "bg": "#F2F5F9",
            "card": "#FFFFFF",
            "text": "#0B1220",
            "muted": "#5B6577",
            "primary": "#1D4ED8",
            "accent": "#10B981",
            "border": "#E6EAF0",
            "shadow": "0 6px 16px rgba(22,38,61,0.08)",
            "done_bg": "rgba(16, 185, 129, 0.10)",
            "pending_bg": "rgba(245, 158, 11, 0.12)",
            "sidebar_bg": "#F8FAFD",
        }

    css = f"""
    <style>
      html, body, .stApp {{
        background: {palette['bg']};
        color: {palette['text']};
      }}

      /* Sidebar styling */
      section[data-testid="stSidebar"] {{
        background: {palette['sidebar_bg']};
        border-right: 1px solid {palette['border']};
        box-shadow: none;
      }}
      section[data-testid="stSidebar"] .block-container {{
        padding-top: 14px;
        padding-bottom: 16px;
      }}

      /* Sidebar components */
      .sb-header {{
        font-size: 12px; font-weight: 700; letter-spacing: .02em; text-transform: uppercase;
        color: {palette['muted']}; margin: 4px 0 6px;
      }}
      .sb-card {{
        border-radius: 12px; border: 1px solid {palette['border']}; background: {palette['card']};
        box-shadow: {palette['shadow']}; padding: 12px 14px; margin-bottom: 10px;
      }}
      .sb-progress {{
        height: 6px; background: {palette['border']}; border-radius: 999px; overflow: hidden; margin: 8px 0 6px;
      }}
      .sb-progress > div {{
        height: 100%; background: {palette['primary']}; border-radius: 999px; transition: width .25s ease;
      }}
      .sb-person {{
        border-radius: 10px; border: 1px solid {palette['border']}; background: {palette['card']};
        padding: 10px 12px; margin-bottom: 8px; box-shadow: {palette['shadow']};
      }}
      .sb-person-name {{ font-size: 13px; font-weight: 600; }}
      .sb-person-stats {{ font-size: 12px; color: {palette['muted']}; margin-top: 4px; }}
      .sb-person-bar {{
        height: 4px; background: {palette['border']}; border-radius: 999px; overflow: hidden; margin-top: 6px;
      }}
      .sb-person-bar > div {{ height: 100%; background: {palette['accent']}; border-radius: 999px; transition: width .25s ease; }}

      /* Main area cards */
      .hero {{
        border-radius: 16px; padding: 18px 22px; background: {palette['card']};
        box-shadow: {palette['shadow']}; border: 1px solid {palette['border']};
      }}
      .chips {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }}
      .chip {{
        font-size: 12px; padding: 6px 10px; border-radius: 999px;
        border: 1px solid {palette['border']}; background: {palette['card']}; color: {palette['muted']};
      }}
      .chip.done {{ color: #10B981; border-color: #10B98133; }}
      .chip.pending {{ color: #F59E0B; border-color: #F59E0B33; }}
      .chip.total {{ color: {palette['primary']}; border-color: {palette['primary']}33; }}

      .task-card {{
        margin: 8px 0; padding: 12px 14px; border-radius: 12px; background: {palette['card']};
        border: 1px solid {palette['border']}; box-shadow: {palette['shadow']};
      }}
      .task-card.done {{ background: {palette['done_bg']}; }}
      .task-card.pending {{ background: {palette['pending_bg']}; }}
      .task-title {{ font-weight: 600; }}
      .task-meta {{ color: {palette['muted']}; font-size: 12px; }}
      .comment {{ font-size: 13px; color: {palette['muted']}; }}

      .soft-label {{ color: {palette['muted']}; font-size: 12px; }}

      /* Sleeker inputs/buttons */
      .stButton > button {{ border-radius: 10px !important; border: 1px solid {palette['border']} !important; }}
      .stTextInput > div > div > input, .stTextArea textarea {{ border-radius: 10px !important; }}
      .stSelectbox > div > div {{ border-radius: 10px !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def person_header(name: str, done: int, pending: int, total: int):
    st.markdown(
        f"""
        <div class=\"hero\">
          <div style=\"display:flex; align-items:center; gap:10px;\">
            <div style=\"font-size: 22px; font-weight: 800;\">👤 {name}’s Tasks</div>
          </div>
          <div class=\"chips\">
            <span class=\"chip done\">{done} done</span>
            <span class=\"chip pending\">{pending} pending</span>
            <span class=\"chip total\">{total} total</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------- Main UI ----------------------

data = load_data()

# Sidebar: appearance + team overview with compact member cards
st.sidebar.markdown("<div class='sb-header'>⚙️ Appearance</div>", unsafe_allow_html=True)
st.session_state.setdefault("dark_mode", False)
if hasattr(st, "toggle"):
    st.session_state.dark_mode = st.sidebar.toggle(
        "Dark mode", value=st.session_state.dark_mode, key="dark_mode_toggle"
    )
else:
    st.session_state.dark_mode = st.sidebar.checkbox(
        "Dark mode", value=st.session_state.dark_mode, key="dark_mode_toggle"
    )

inject_styles(bool(st.session_state.dark_mode))

team_done = 0
team_pending = 0
team_total = 0
for p in PEOPLE:
    d, pnd, ttl = counts(data[p]["tasks"])
    team_done += d
    team_pending += pnd
    team_total += ttl

ratio = team_done / team_total if team_total else 0.0
st.sidebar.markdown(
    f"""
    <div class='sb-card'>
      <div style='font-weight:700;'>Team Overview</div>
      <div class='sb-progress'><div style='width:{ratio*100:.0f}%'></div></div>
      <div class='soft-label'>{team_done}/{team_total} done</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("<div class='sb-header'>👥 Members</div>", unsafe_allow_html=True)
for p in PEOPLE:
    d, pnd, ttl = counts(data[p]["tasks"])
    percent = (d / ttl * 100) if ttl else 0.0
    st.sidebar.markdown(
        f"""
        <div class='sb-person'>
          <div class='sb-person-name'>{LABELS[p]}</div>
          <div class='sb-person-bar'><div style='width:{percent:.0f}%'></div></div>
          <div class='sb-person-stats'>{d} done • {pnd} pending</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.title("🎯 Team ToDo")
st.caption("Modern UI • Add, remove, comment, and track done/pending for Santosh, Vishal, and Sagar.")

# Tabs per person
labels = [LABELS[p] for p in PEOPLE]
tabs = st.tabs(labels)

for idx, person in enumerate(PEOPLE):
    with tabs[idx]:
        tasks = list(data[person]["tasks"])  # shallow copy for safe iteration
        done, pending, total = counts(tasks)
        person_header(LABELS[person], done, pending, total)

        # Controls row: filter, sort, search
        c1, c2, c3 = st.columns([0.20, 0.20, 0.60])
        with c1:
            view = st.selectbox(
                "Filter",
                ["All", "Pending", "Done"],
                index=0,
                help="Show tasks by status",
                key=f"view_{person}",
            )
        with c2:
            sort = st.selectbox(
                "Sort",
                ["Newest first", "Oldest first", "A–Z", "Z–A"],
                index=0,
                key=f"sort_{person}",
            )
        with c3:
            query = st.text_input(
                "Search",
                placeholder="Type to filter tasks by title…",
                key=f"query_{person}",
            )

        # Add task form in an expander
        with st.expander("➕ Add a new task", expanded=False):
            with st.form(key=f"add_{person}", clear_on_submit=True):
                title = st.text_input("Task title", key=f"title_{person}")
                comment = st.text_area("Initial comment (optional)", key=f"comment_{person}", height=80)
                submitted = st.form_submit_button("Add Task")
                if submitted:
                    if title and title.strip():
                        add_task(data, person, title, comment)
                        st.success("Task added.")
                        st.rerun()
                    else:
                        st.warning("Please enter a task title.")

        # Apply filter & search
        def match_view(t):
            if view == "All":
                return True
            if view == "Pending":
                return t.get("status") == "pending"
            if view == "Done":
                return t.get("status") == "done"
            return True

        def match_query(t):
            if not query:
                return True
            return query.lower().strip() in t["title"].lower()

        filtered = [t for t in tasks if match_view(t) and match_query(t)]

        # Sort
        if sort == "Newest first":
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort == "Oldest first":
            filtered.sort(key=lambda x: x.get("created_at", ""))
        elif sort == "A–Z":
            filtered.sort(key=lambda x: x.get("title", "").lower())
        elif sort == "Z–A":
            filtered.sort(key=lambda x: x.get("title", "").lower(), reverse=True)

        # Progress bar
        st.progress(done / total if total else 0.0)

        if not filtered:
            st.info("No tasks match the current filters. Try adding a new task or clearing filters.")
        else:
            for t in filtered:
                # Card wrapper (for modern visuals)
                card_state = "done" if t.get("status") == "done" else "pending"
                st.markdown(f"<div class='task-card {card_state}'>", unsafe_allow_html=True)

                # Row layout: checkbox | title/comments | actions
                cols = st.columns([0.08, 0.64, 0.28])

                with cols[0]:
                    checked = t.get("status") == "done"
                    new_checked = st.checkbox(
                        "Done",
                        value=checked,
                        key=f"chk_{person}_{t['id']}",
                        help="Mark done/pending",
                    )
                    if new_checked != checked:
                        set_status(data, person, t["id"], "done" if new_checked else "pending")
                        st.rerun()

                with cols[1]:
                    st.markdown(f"<div class='task-title'>{t['title']}</div>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div class='task-meta'>Created at: {t.get('created_at', '')}</div>",
                        unsafe_allow_html=True,
                    )
                    # Comments expander
                    if t.get("comments"):
                        with st.expander("💬 Comments", expanded=False):
                            for c in t["comments"]:
                                st.markdown(
                                    f"<div class='comment'>• {c['text']} <span class='task-meta'>(at {c['ts']})</span></div>",
                                    unsafe_allow_html=True,
                                )

                with cols[2]:
                    # Delete task
                    delete_col, comment_col = st.columns(2)
                    with delete_col:
                        if st.button("🗑️ Delete", key=f"del_{person}_{t['id']}"):
                            remove_task(data, person, t["id"])
                            st.rerun()
                    with comment_col:
                        with st.form(key=f"cmt_{person}_{t['id']}", clear_on_submit=True):
                            ctext = st.text_input("Add comment", key=f"ct_{person}_{t['id']}")
                            csubmit = st.form_submit_button("Add")
                            if csubmit and ctext and ctext.strip():
                                add_comment(data, person, t["id"], ctext)
                                st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# Helpful note
st.caption(
    "Data is saved to `todo_data.json` next to this file. You can back it up or edit it if needed."
)
