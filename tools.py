from database import add_expense, get_total, get_all_expenses


def add_expense_tool(category, amount):
    add_expense(category, amount)
    return f"Added ₹{amount} to {category}"


def total_expense_tool():
    total = get_total()
    return f"Total Expenses = ₹{total}"


def list_expenses_tool():
    expenses = get_all_expenses()
    if not expenses:
        return "No expenses recorded yet."
    
    result = "Here are your expenses:\n"
    for cat, amt in expenses:
        result += f"- {cat}: ₹{amt}\n"
    return result.strip()