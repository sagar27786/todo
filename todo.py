import os
import json
import uuid
from datetime import datetime
import streamlit as st

# Team ToDo app for Santosh, Vishal, and Sagar
# Persists tasks, comments, and status across runs using a JSON file

PEOPLE = ["santosh", "vishal", "sagar"]
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


# ---------------------- UI ----------------------

st.title("🎯 Team ToDo")
st.caption("Add, remove, comment, and track done/pending for Santosh, Vishal, and Sagar.")

data = load_data()

# Sidebar: overall metrics
st.sidebar.header("Team Overview")
team_done = 0
team_pending = 0
team_total = 0
for p in PEOPLE:
    d, pnd, ttl = counts(data[p]["tasks"])
    st.sidebar.metric(p.capitalize(), f"{d} done / {pnd} pending", help=f"Total: {ttl}")
    team_done += d
    team_pending += pnd
    team_total += ttl

if team_total > 0:
    st.sidebar.progress(team_done / team_total)
st.sidebar.write(f"**Team Progress:** {team_done}/{team_total} done")

# Tabs per person
labels = ["Santosh", "Vishal", "Sagar"]
tabs = st.tabs(labels)

for idx, person in enumerate(PEOPLE):
    with tabs[idx]:
        st.subheader(f"{labels[idx]}’s Tasks")

        # Add task form
        with st.form(key=f"add_{person}", clear_on_submit=True):
            title = st.text_input("Task title", key=f"title_{person}")
            comment = st.text_area("Comment (optional)", key=f"comment_{person}", height=80)
            submitted = st.form_submit_button("Add Task")
            if submitted:
                if title and title.strip():
                    add_task(data, person, title, comment)
                    st.success("Task added.")
                    st.rerun()
                else:
                    st.warning("Please enter a task title.")

        tasks = list(data[person]["tasks"])  # shallow copy for safe iteration
        done, pending, total = counts(tasks)
        st.write(f"Progress: **{done} done / {pending} pending** (Total: {total})")
        if total > 0:
            st.progress(done / total)

        if not tasks:
            st.info("No tasks yet. Add one above.")
        else:
            for t in tasks:
                # Row layout: checkbox | title/comments | actions
                cols = st.columns([0.06, 0.64, 0.30])

                with cols[0]:
                    checked = t.get("status") == "done"
                    new_checked = st.checkbox(
                        "",
                        value=checked,
                        key=f"chk_{person}_{t['id']}",
                        help="Mark done/pending",
                    )
                    if new_checked != checked:
                        set_status(data, person, t["id"], "done" if new_checked else "pending")
                        st.rerun()

                with cols[1]:
                    st.markdown(f"**{t['title']}**")
                    # Comments expander
                    if t.get("comments"):
                        with st.expander("Comments", expanded=False):
                            for c in t["comments"]:
                                st.write(f"- {c['text']}  _(at {c['ts']})_")

                with cols[2]:
                    # Delete task
                    if st.button("🗑️ Delete", key=f"del_{person}_{t['id']}"):
                        remove_task(data, person, t["id"])
                        st.rerun()

                    # Add comment form
                    with st.form(key=f"cmt_{person}_{t['id']}", clear_on_submit=True):
                        ctext = st.text_input("Add comment", key=f"ct_{person}_{t['id']}")
                        csubmit = st.form_submit_button("Add Comment")
                        if csubmit and ctext and ctext.strip():
                            add_comment(data, person, t["id"], ctext)
                            st.rerun()

# Helpful note
st.caption(
    "Data is saved to `todo_data.json` next to this file. You can back it up or edit it if needed."
)
