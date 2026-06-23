import sqlite3


def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        amount REAL
    )
    """)
    conn.commit()
    conn.close()


init_db()


def add_expense(category, amount):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses(category, amount) VALUES (?, ?)",
        (category, amount)
    )
    conn.commit()
    conn.close()


def get_total():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0


def get_all_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount FROM expenses")
    result = cursor.fetchall()
    conn.close()
    return result


# --- Added for the web UI (does not change any existing behaviour above) ---

def get_expenses_with_id():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, amount FROM expenses ORDER BY id DESC")
    result = cursor.fetchall()
    conn.close()
    return result


def delete_expense(expense_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def get_category_totals():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
    )
    result = cursor.fetchall()
    conn.close()
    return result