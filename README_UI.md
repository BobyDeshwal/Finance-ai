# Pocket Ledger — web UI for the Personal Finance Agent

This adds a pastel browser UI on top of your existing CLI agent. Nothing
about `app.py`, `agent.py`, or `tools.py` was changed — `database.py` only
got three small *additional* functions (nothing removed), so the original
`python app.py` CLI still works exactly as before.

## Run it

```bash
pip install -r requirements.txt
python web_app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## What's in the UI

- **Ledger tab** — a receipt-style total at the top, pastel chips showing
  spend per category, a form to add a new expense, and a scrollable list
  of recent expenses (with a one-click remove on each).
- **Ask the agent tab** — a chat window wired to your existing
  `agent.py` / Gemini setup, so you can still say things like
  *"I spent 200 on groceries"* and have it logged for you.

If the chat tab shows a connection error, check that `GEMINI_API_KEY` in
your `.env` file is valid and that you have network access to the Gemini
API from this machine.

## New files

- `web_app.py` — Flask routes (`/`, `/api/summary`, `/api/add`,
  `/api/delete/<id>`, `/api/chat`)
- `templates/index.html`, `static/style.css`, `static/app.js` — the UI
- `requirements.txt` — `flask`, `google-genai`, `python-dotenv`
