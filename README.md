# Team ToDo (Streamlit)

A simple, persistent team ToDo app for Santosh, Vishal, and Sagar.

## Features
- Separate tabs for three people
- Add/remove tasks and add comments
- Mark done/pending with progress bars
- Team overview in sidebar
- Local persistence via `todo_data.json`

## Run Locally
```
python -m streamlit run todo.py
```
The app opens at `http://localhost:8501/`.

## Deployment via GitHub + Streamlit Cloud
1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io/ and connect your GitHub.
3. Select the repo and set:
   - App file: `todo.py`
   - Python version: auto
   - Requirements: uses `requirements.txt`
4. Deploy.

### Note on Persistence in Cloud
This app saves data to `todo_data.json`. On Streamlit Cloud, the file system is ephemeral, so data may reset after a restart. For true cloud persistence, plug in a hosted DB (e.g., Supabase, Deta Base). Happy to add that.