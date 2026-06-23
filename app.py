import sys
from agent import run_agent

# Reconfigure stdout/stderr to handle UTF-8/emojis safely on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

print("=== Personal Finance Agent ===")
print("Type 'exit' to quit.\n")

while True:
    try:
        user = input("You: ")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        break

    if user.strip().lower() == "exit":
        print("Goodbye!")
        break

    if not user.strip():
        continue

    response = run_agent(user)

    print("\nAgent:", response)