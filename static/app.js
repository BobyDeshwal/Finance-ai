(() => {
  const PALETTE = [
    { bg: "var(--mint)", deep: "var(--mint-deep)" },
    { bg: "var(--peach)", deep: "var(--peach-deep)" },
    { bg: "var(--sky)", deep: "var(--sky-deep)" },
    { bg: "var(--lilac)", deep: "var(--lilac-deep)" },
    { bg: "var(--rose)", deep: "var(--rose-deep)" },
    { bg: "var(--butter)", deep: "var(--butter-deep)" },
  ];

  function colorFor(category) {
    let hash = 0;
    for (const ch of category) hash = (hash * 31 + ch.charCodeAt(0)) % 9973;
    return PALETTE[hash % PALETTE.length];
  }

  function formatRupees(value) {
    const n = Number(value) || 0;
    return n.toLocaleString("en-IN", {
      minimumFractionDigits: n % 1 === 0 ? 0 : 2,
      maximumFractionDigits: 2,
    });
  }

  const totalAmountEl = document.getElementById("totalAmount");
  const entryCountEl = document.getElementById("entryCount");
  const chipsEl = document.getElementById("categoryChips");
  const listEl = document.getElementById("expenseList");
  const emptyEl = document.getElementById("emptyState");
  const formMsgEl = document.getElementById("formMsg");
  const addForm = document.getElementById("addForm");

  async function refresh() {
    const res = await fetch("/api/summary");
    const data = await res.json();

    totalAmountEl.textContent = formatRupees(data.total);
    entryCountEl.textContent = `${data.expenses.length} entr${data.expenses.length === 1 ? "y" : "ies"}`;

    chipsEl.innerHTML = "";
    data.categories.forEach(({ category, amount }) => {
      const c = colorFor(category);
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.style.background = c.bg;
      chip.style.color = c.deep;
      chip.innerHTML = `${category} <span class="chip-amount">₹${formatRupees(amount)}</span>`;
      chipsEl.appendChild(chip);
    });

    listEl.innerHTML = "";
    emptyEl.hidden = data.expenses.length > 0;

    data.expenses.forEach(({ id, category, amount }) => {
      const c = colorFor(category);
      const li = document.createElement("li");
      li.className = "receipt-item";
      li.style.borderLeftColor = c.deep;
      li.innerHTML = `
        <span class="dot" style="background:${c.deep}"></span>
        <span class="item-category">${category}</span>
        <span class="item-amount">₹${formatRupees(amount)}</span>
        <button class="delete-btn" title="Remove" aria-label="Remove ${category}">×</button>
      `;
      li.querySelector(".delete-btn").addEventListener("click", async () => {
        await fetch(`/api/delete/${id}`, { method: "POST" });
        refresh();
      });
      listEl.appendChild(li);
    });
  }

  addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const category = document.getElementById("category").value.trim();
    const amount = document.getElementById("amount").value;

    formMsgEl.textContent = "";
    formMsgEl.className = "form-msg";

    const res = await fetch("/api/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, amount }),
    });
    const data = await res.json();

    if (!res.ok) {
      formMsgEl.textContent = data.error || "Something went wrong.";
      formMsgEl.classList.add("error");
      return;
    }

    formMsgEl.textContent = `Added ₹${formatRupees(amount)} to ${category}.`;
    formMsgEl.classList.add("success");
    addForm.reset();
    refresh();
  });

  // ---- Tabs ----
  const tabBtns = document.querySelectorAll(".tab-btn");
  const panels = {
    ledger: document.getElementById("ledger-panel"),
    chat: document.getElementById("chat-panel"),
  };

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => {
        b.classList.toggle("active", b === btn);
        b.setAttribute("aria-selected", b === btn ? "true" : "false");
      });
      Object.entries(panels).forEach(([key, el]) => {
        el.hidden = key !== btn.dataset.tab;
      });
    });
  });

  // ---- Chat ----
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatWindow = document.getElementById("chatWindow");

  function addBubble(text, who, pending = false) {
    const div = document.createElement("div");
    div.className = `bubble ${who}${pending ? " pending" : ""}`;
    div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return div;
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    addBubble(message, "user");
    chatInput.value = "";
    const pending = addBubble("…thinking", "agent", true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      pending.textContent = data.reply || data.error || "No response.";
      pending.classList.remove("pending");
      refresh();
    } catch (err) {
      pending.textContent = "Couldn't reach the server.";
      pending.classList.remove("pending");
    }
  });

  refresh();
})();
