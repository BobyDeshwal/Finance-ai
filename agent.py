import os
import json
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import errors

from tools import (
    add_expense_tool,
    total_expense_tool,
    list_expenses_tool
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

SYSTEM_PROMPT = """
You are a Personal Finance Agent.

Available tools:

1. add_expense_tool(category, amount)
2. total_expense_tool()
3. list_expenses_tool()

When a tool is needed, return ONLY JSON.

Examples:

{
  "tool":"add_expense_tool",
  "category":"food",
  "amount":500
}

or

{
  "tool":"total_expense_tool"
}

or

{
  "tool":"list_expenses_tool"
}
"""


def extract_json(text):
    """Robust JSON extraction from text response."""
    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    return json.loads(text)


def generate_content_with_retry(client, model, contents, max_retries=5, initial_delay=2.0, backoff_factor=2.0):
    """Generate content with exponential backoff on rate limits and intermittent server errors."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents
            )
            return response
        except errors.APIError as e:
            if e.code in [429, 503] or "quota" in str(e).lower() or "limit" in str(e).lower():
                if attempt == max_retries - 1:
                    raise e
                sleep_time = delay + random.uniform(0, 1.0)
                print(f"\n[API Warning] Received error {e.code}. Retrying in {sleep_time:.2f}s (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_time)
                delay *= backoff_factor
            else:
                raise e
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            sleep_time = delay + random.uniform(0, 1.0)
            print(f"\n[Connection Warning] {e}. Retrying in {sleep_time:.2f}s (Attempt {attempt + 1}/{max_retries})...")
            time.sleep(sleep_time)
            delay *= backoff_factor


def run_agent(user_query):
    try:
        response = generate_content_with_retry(
            client=client,
            model="gemini-3.5-flash",
            contents=f"{SYSTEM_PROMPT}\nUser:{user_query}"
        )
    except Exception as e:
        return f"Error communicating with Gemini API: {e}"

    text = response.text.strip()

    try:
        data = extract_json(text)
        tool = data.get("tool")

        if tool == "add_expense_tool":
            # Extract and validate amount
            amount_val = data.get("amount")
            try:
                amount = float(amount_val)
            except (ValueError, TypeError):
                return f"Invalid amount: {amount_val}"

            result = add_expense_tool(
                data.get("category", "other"),
                amount
            )

        elif tool == "total_expense_tool":
            result = total_expense_tool()

        elif tool == "list_expenses_tool":
            result = list_expenses_tool()

        else:
            result = "Unknown Tool"

        return result

    except Exception:
        # If it wasn't JSON or extraction failed, return the text response directly
        return text