# Team Availability Tracker

A polished, responsive team status dashboard built with **Python, Flask, SQLite, HTML, CSS, and vanilla JavaScript**. This project is designed to match the VirtualWorks task: a list of users with availability toggles that update a boolean value in the database and immediately reflect the saved state in the UI.

## Features

- Responsive dashboard with team, available, and busy summary cards
- Six sample team members seeded into SQLite automatically
- Toggle availability on/off; the browser sends a `PATCH` request to Flask
- SQLite persists each status change across refreshes and app restarts
- Search by team member name and filter by Everyone / Available / Busy
- Loading/sync state, error feedback, and success toast
- Accessible input labels, keyboard shortcut (`Ctrl+K` / `Cmd+K`), and responsive layout
- JSON API and automated tests

## Requirements

- Windows 10/11
- Python 3.10 or newer (Python 3.11 or 3.12 recommended)
- Internet connection only if you want the optional Google Fonts to load; the app works without them

SQLite is included with standard Python builds. You do **not** need to install SQLite separately or install Node.js/npm.

## Run on Windows (PowerShell)

1. Extract `team-availability-tracker.zip` to a folder, for example `C:\Users\YourName\Projects\team-availability-tracker`.
2. Open PowerShell in that folder. In VS Code, use **File → Open Folder**, then **Terminal → New Terminal**.
3. Check Python:

   ```powershell
   py --version
   ```

4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation for this terminal, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again. This affects only the current PowerShell process.

5. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python app.py
   ```

7. Open **http://127.0.0.1:5000** in Chrome. Leave the terminal running while using the app.

The `instance` folder and `availability.db` database are created automatically on first launch. On later launches, existing availability statuses are retained.

## Test it

In a second PowerShell terminal, activate the same environment and run:

```powershell
python -m unittest discover -s tests -v
```

Five tests cover dashboard rendering, API listing, persisted updates, invalid payloads, and missing team members.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Render dashboard |
| `GET` | `/api/members` | Return team members and summary counts as JSON |
| `PATCH` | `/api/members/<id>/availability` | Persist `{"is_available": true}` or `false` |
| `GET` | `/health` | Basic health check |

Example PowerShell request:

```powershell
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:5000/api/members/1/availability -ContentType 'application/json' -Body '{"is_available":false}'
```

## Project structure

```text
team-availability-tracker/
├── app.py                 # Flask routes, database setup, and API
├── requirements.txt       # Python dependencies
├── README.md              # Setup and usage guide
├── instance/              # Auto-created SQLite database directory
├── templates/
│   └── index.html         # Jinja dashboard template
├── static/
│   ├── css/style.css      # Responsive visual design
│   └── js/main.js         # Search, filters, toggles, and API sync
└── tests/
    └── test_app.py        # Automated tests
```

## How the availability toggle works

1. Flask reads each team member from SQLite and renders the page using Jinja.
2. A toggle change triggers JavaScript `fetch()` with a `PATCH` request.
3. Flask validates that `is_available` is a real JSON boolean, updates SQLite, and returns the saved member record.
4. JavaScript updates the row badge, last-updated label, summary counts, and sync indicator. If the request fails, the toggle is reverted and an error message appears.

## Notes before submission

- This is a local demo with seeded example users, not a multi-user authenticated production service.
- The `SECRET_KEY` default is for local development only. Set a strong environment variable before deploying publicly.
- The included sample names and statuses are demo data; edit `SEED_USERS` in `app.py` if your assignment needs different sample users. Existing database rows are not overwritten on startup.
- Do not submit the generated `.venv` folder. The ZIP intentionally excludes it; dependencies install from `requirements.txt`.
