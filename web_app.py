"""
Pocket Ledger — a small web UI for the Personal Finance Agent.

Run with:
    python web_app.py
Then open http://127.0.0.1:5000 in your browser.

This file does not change any of the existing CLI behaviour in app.py —
it just gives the same database and agent a pastel face.
"""

from flask import Flask, render_template, request, jsonify

from database import (
    add_expense,
    get_total,
    get_expenses_with_id,
    delete_expense,
    get_category_totals,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def api_summary():
    expenses = get_expenses_with_id()
    categories = get_category_totals()
    return jsonify(
        {
            "total": get_total(),
            "expenses": [
                {"id": e_id, "category": cat, "amount": amt}
                for e_id, cat, amt in expenses
            ],
            "categories": [
                {"category": cat, "amount": amt} for cat, amt in categories
            ],
        }
    )


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json(silent=True) or {}
    category = (data.get("category") or "other").strip() or "other"

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "That doesn't look like a number."}), 400

    if amount <= 0:
        return jsonify({"error": "Amount needs to be greater than zero."}), 400

    add_expense(category, amount)
    return jsonify({"ok": True})


@app.route("/api/delete/<int:expense_id>", methods=["POST"])
def api_delete(expense_id):
    delete_expense(expense_id)
    return jsonify({"ok": True})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Say something first!"}), 400

    try:
        # Imported lazily so the rest of the UI still works even if the
        # Gemini client can't be created (e.g. missing API key).
        from agent import run_agent

        reply = run_agent(message)
    except Exception as exc:  # noqa: BLE001 - surface any failure to the chat UI
        reply = (
            "I couldn't reach the agent just now "
            f"({exc}). Check the GEMINI_API_KEY in your .env file."
        )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
