// =========================================================
// SMARTLOAN TRIGGER — COMPLETE JAVASCRIPT
// PART 1: SETUP + LOGIN + LOAD + CLASS LOGIC
// =========================================================

console.log("🚀 SmartLoan Trigger App.js loaded!");

// =========================================================
// GLOBAL STATE
// =========================================================

let allCustomers = [];
let currentClass = "LOW";
let filteredCustomers = [];
let currentPage = 1;
const ROWS_PER_PAGE = 50;
let currentCustomer = null;

// Chart instances
let pieChartInstance = null;
let barChartInstance = null;

// Call timer
let callTimerInterval = null;
let callSeconds = 0;

// History data
let currentHistoryData = { actions: [], offers: [] };

// Class name mapping
const CLASS_MAP = {
    "LOW": "LOW",
    "MIDDLE": "MEDIUM",
    "MEDIUM": "MEDIUM",
    "HIGH": "HIGH"
};

// =========================================================
// DOM READY
// =========================================================

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM Ready");

    setupBrightnessSlider();
    setupLoginForm();
    setupLogoutButton();
    setupRefreshButton();
    setupSearchBox();
    setupPaginationButtons();
    setupOfferInputs();
    setupCallModal();
    setupSmsModal();
    setupHistoryModal();
    setupLoanConfirmModal();
    setupModalCloseButtons();
    setupGlobalClickHandlers();
});

// =========================================================
// LAMP BRIGHTNESS SLIDER
// =========================================================

function setupBrightnessSlider() {
    const slider = document.getElementById("brightness");
    const shade = document.getElementById("shade");
    const glow = document.getElementById("glow");
    const loginCard = document.querySelector(".login-card");

    if (!slider) return;

    function updateBrightness() {
        const val = parseInt(slider.value) / 100;

        if (shade) shade.style.filter = `brightness(${0.3 + val * 1.5})`;
        if (glow) glow.style.opacity = String(0.05 + val * 1.0);
        if (loginCard) loginCard.style.filter = `brightness(${0.5 + val * 0.7})`;
    }

    slider.addEventListener("input", updateBrightness);
    updateBrightness();
}

// =========================================================
// LOGIN FORM
// =========================================================

function setupLoginForm() {
    const form = document.getElementById("loginForm");
    const btn = document.getElementById("loginBtn");

    if (!form || !btn) return;

    async function doLogin(e) {
        if (e) e.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();
        const errorEl = document.getElementById("loginError");

        if (!username || !password) {
            if (errorEl) errorEl.textContent = "Please enter username and password.";
            return;
        }

        if (errorEl) errorEl.textContent = "";

        document.getElementById("login-screen").style.display = "none";
        document.getElementById("dashboard").style.display = "block";

        const welcome = document.getElementById("welcomeText");
        if (welcome) welcome.textContent = "👋 Welcome, " + username;

        await loadCustomers();
    }

    btn.addEventListener("click", doLogin);
    form.addEventListener("submit", doLogin);
}

// =========================================================
// LOGOUT
// =========================================================

function setupLogoutButton() {
    const btn = document.getElementById("logoutBtn");
    if (!btn) return;

    btn.addEventListener("click", function () {
        document.getElementById("dashboard").style.display = "none";
        document.getElementById("login-screen").style.display = "flex";

        const username = document.getElementById("username");
        const password = document.getElementById("password");
        const error = document.getElementById("loginError");

        if (username) username.value = "";
        if (password) password.value = "";
        if (error) error.textContent = "";

        allCustomers = [];
        currentCustomer = null;
        currentPage = 1;
    });
}

// =========================================================
// REFRESH BUTTON
// =========================================================

function setupRefreshButton() {
    const btn = document.getElementById("refreshBtn");
    if (!btn) return;

    btn.addEventListener("click", function () {
        loadCustomers();
    });
}

// =========================================================
// SEARCH BOX
// =========================================================

function setupSearchBox() {
    const box = document.getElementById("search");
    if (!box) return;

    box.addEventListener("input", function (e) {
        const query = e.target.value.trim();

        if (query === "") {
            currentPage = 1;
            applyClassFilter();
        } else {
            searchCustomer(query);
        }
    });
}

// =========================================================
// LOAD CUSTOMERS FROM API
// =========================================================

async function loadCustomers() {
    const status = document.getElementById("status");
    const btn = document.getElementById("refreshBtn");

    if (btn) {
        btn.disabled = true;
        btn.textContent = "⏳ Loading...";
    }

    if (status) {
        status.textContent = "Loading customer data...";
        status.className = "status";
    }

    try {
        const response = await fetch("/api/customers", {
            method: "GET",
            headers: { "Accept": "application/json" },
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("API Error: " + response.status);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Failed to load");
        }

        allCustomers = data.customers || [];
        const stats = data.stats || {};

        console.log("✅ Loaded:", allCustomers.length);
        console.log("📊 Stats:", stats);

        updateClassCounts(stats, allCustomers.length);
        renderCharts(stats);

        currentClass = "LOW";
        currentPage = 1;
        selectCustomerClass("LOW");

        if (status) {
            status.textContent = `${allCustomers.length} customers loaded successfully.`;
            status.className = "status success";
        }

    } catch (err) {
        console.error("❌ Error:", err);

        if (status) {
            status.textContent = "Error: " + err.message;
            status.className = "status error";
        }

        const rows = document.getElementById("customerRows");
        if (rows) {
            rows.innerHTML = `<tr><td colspan="9" class="empty">${err.message}</td></tr>`;
        }

    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = "🔄 Refresh Data";
        }
    }
}

// =========================================================
// UPDATE CLASS COUNTS
// =========================================================

function updateClassCounts(stats, total) {
    setText("lowCount", stats.LOW || 0);
    setText("middleCount", stats.MEDIUM || 0);
    setText("highCount", stats.HIGH || 0);

    setText("total", total || 0);
    setText("contactNow", stats.HIGH || 0);
    setText("softReminder", stats.MEDIUM || 0);
    setText("wait", stats.LOW || 0);
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

// =========================================================
// CLASS DETECTION
// =========================================================

function getCustomerClass(customer) {
    // Backend ka bheja hua class use karo
    const backendClass = String(customer.customer_class || "").toUpperCase();
    if (["LOW", "MEDIUM", "HIGH"].includes(backendClass)) {
        return backendClass;
    }

    // Fallback (agar backend class na de)
    const balance = parseFloat(customer.balance) || 0;
    if (balance < 2000) return "LOW";
    if (balance < 5000) return "MEDIUM";
    return "HIGH";
}

// =========================================================
// SELECT CUSTOMER CLASS
// =========================================================

function selectCustomerClass(cls) {
    currentClass = cls;
    currentPage = 1;

    document.querySelectorAll(".class-card").forEach(c => c.classList.remove("active"));

    const cardMap = {
        "LOW": "lowClassCard",
        "MIDDLE": "middleClassCard",
        "HIGH": "highClassCard"
    };

    const cardId = cardMap[cls];
    if (cardId) {
        const card = document.getElementById(cardId);
        if (card) card.classList.add("active");
    }

    const label = document.getElementById("selectedClassLabel");
    if (label) {
        if (cls === "LOW") label.textContent = "LOW CLASS / Lower Income Group";
        else if (cls === "MIDDLE") label.textContent = "MIDDLE CLASS / Middle Income Group";
        else label.textContent = "HIGH CLASS / HNI / Premium";
    }

    const title = document.getElementById("customerListTitle");
    if (title) title.textContent = cls + " CLASS — Customer Priority List";

    applyClassFilter();
}

// =========================================================
// APPLY CLASS FILTER
// =========================================================

function applyClassFilter() {
    const backendClass = CLASS_MAP[currentClass] || currentClass;

    filteredCustomers = allCustomers.filter(c =>
        getCustomerClass(c) === backendClass
    );

    console.log(`Filter: ${currentClass} → ${backendClass} | Matched: ${filteredCustomers.length}`);

    updateTableCount();
    renderTable();
    updatePagination();
}

// =========================================================
// UPDATE TABLE COUNT
// =========================================================

function updateTableCount() {
    const el = document.getElementById("tableCount");
    if (el) el.textContent = filteredCustomers.length + " customers";
}

// =========================================================
// FORMAT HELPERS
// =========================================================

function formatBalance(balance) {
    if (balance === "" || balance === null || balance === undefined) return "₹0";
    const num = parseFloat(balance);
    if (isNaN(num)) return "₹" + balance;
    return "₹" + num.toLocaleString("en-IN");
}

function formatAction(action) {
    if (!action) return "";
    if (action === "Contact Now") return `<span class="badge badge-now">Contact Now</span>`;
    if (action === "Soft Reminder") return `<span class="badge badge-soft">Soft Reminder</span>`;
    if (action === "Occasional Offer") return `<span class="badge badge-soft">Occasional Offer</span>`;
    return `<span class="badge badge-wait">${action}</span>`;
}

// =========================================================
// END OF PART 1
// =========================================================
// =========================================================
// PART 2: TABLE + PAGINATION + SEARCH + CUSTOMER MODAL
// =========================================================

// =========================================================
// RENDER TABLE (With Pagination)
// =========================================================

function renderTable() {
    const tbody = document.getElementById("customerRows");
    if (!tbody) return;

    if (filteredCustomers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="empty">No customers found in ${currentClass} class.</td></tr>`;
        return;
    }

    const totalPages = Math.ceil(filteredCustomers.length / ROWS_PER_PAGE);
    if (currentPage > totalPages) currentPage = totalPages;

    const start = (currentPage - 1) * ROWS_PER_PAGE;
    const end = start + ROWS_PER_PAGE;
    const pageData = filteredCustomers.slice(start, end);

    tbody.innerHTML = "";

    pageData.forEach(c => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";

        tr.addEventListener("click", function () {
            openCustomerModal(c);
        });

        tr.innerHTML = `
            <td>${c.customer_id || ""}</td>
            <td>${c.age || ""}</td>
            <td>${c.job || ""}</td>
            <td>${c.marital || ""}</td>
            <td>${c.education || ""}</td>
            <td>${formatBalance(c.balance)}</td>
            <td class="score">${c.right_time_score || 0}%</td>
            <td>${formatAction(c.recommended_action)}</td>
            <td>${c.channel || ""}</td>
        `;

        tbody.appendChild(tr);
    });

    updatePagination();
}

// =========================================================
// SEARCH CUSTOMER
// =========================================================

function searchCustomer(query) {
    const tbody = document.getElementById("customerRows");
    if (!tbody) return;

    const q = query.toUpperCase();
    const results = allCustomers.filter(c =>
        String(c.customer_id || "").toUpperCase().includes(q)
    );

    if (results.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="empty">No customer found for "${query}"</td></tr>`;
        return;
    }

    tbody.innerHTML = "";

    results.slice(0, 100).forEach(c => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";

        tr.addEventListener("click", function () {
            openCustomerModal(c);
        });

        tr.innerHTML = `
            <td>${c.customer_id}</td>
            <td>${c.age || ""}</td>
            <td>${c.job || ""}</td>
            <td>${c.marital || ""}</td>
            <td>${c.education || ""}</td>
            <td>${formatBalance(c.balance)}</td>
            <td class="score">${c.right_time_score || 0}%</td>
            <td>${formatAction(c.recommended_action)}</td>
            <td>${c.channel || ""}</td>
        `;

        tbody.appendChild(tr);
    });
}

// =========================================================
// PAGINATION
// =========================================================

function setupPaginationButtons() {
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            const totalPages = Math.ceil(filteredCustomers.length / ROWS_PER_PAGE);
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });
    }
}

function updatePagination() {
    const totalPages = Math.max(1, Math.ceil(filteredCustomers.length / ROWS_PER_PAGE));

    setText("pageInfo", `Page ${currentPage} of ${totalPages}`);

    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");

    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
}

// =========================================================
// CUSTOMER MODAL — OPEN
// =========================================================

function openCustomerModal(customer) {
    const modal = document.getElementById("customerModal");
    const details = document.getElementById("customerDetails");

    if (!modal || !details) return;

    currentCustomer = customer;

    const customerId = customer.customer_id || "-";
    const age = customer.age ?? "-";
    const job = customer.job ?? "-";
    const marital = customer.marital ?? "-";
    const education = customer.education ?? "-";
    const balance = customer.balance ?? 0;
    const cls = getCustomerClass(customer);
    const score = customer.right_time_score ?? 0;
    const action = customer.recommended_action || "-";

    details.innerHTML = `
        <div class="detail">
            <small>Customer ID</small>
            <strong>${customerId}</strong>
        </div>
        <div class="detail">
            <small>Class</small>
            <strong>${cls}</strong>
        </div>
        <div class="detail">
            <small>Age</small>
            <strong>${age}</strong>
        </div>
        <div class="detail">
            <small>Job</small>
            <strong>${job}</strong>
        </div>
        <div class="detail">
            <small>Marital</small>
            <strong>${marital}</strong>
        </div>
        <div class="detail">
            <small>Education</small>
            <strong>${education}</strong>
        </div>
        <div class="detail">
            <small>Balance</small>
            <strong>${formatBalance(balance)}</strong>
        </div>
        <div class="detail">
            <small>Right-Time Score</small>
            <strong>${score}%</strong>
        </div>
        <div class="detail">
            <small>Recommended Action</small>
            <strong>${action}</strong>
        </div>
    `;

    // Class-based loan defaults
    const amountInput = document.getElementById("offerAmount");
    const rateInput = document.getElementById("interestRate");

    if (amountInput) {
        if (cls === "HIGH") amountInput.value = 500000;
        else if (cls === "MEDIUM") amountInput.value = 250000;
        else amountInput.value = 100000;
    }

    if (rateInput) {
        if (cls === "HIGH") rateInput.value = 9.5;
        else if (cls === "MEDIUM") rateInput.value = 10.5;
        else rateInput.value = 12.0;
    }

    const msg = document.getElementById("actionMessage");
    if (msg) {
        msg.textContent = "";
        msg.className = "action-message";
    }

    updateEmiPreview();
    modal.classList.add("active");
}

// =========================================================
// CUSTOMER MODAL — CLOSE
// =========================================================

function closeCustomerModal() {
    const modal = document.getElementById("customerModal");
    if (modal) modal.classList.remove("active");
    currentCustomer = null;
}

// =========================================================
// SETUP MODAL CLOSE BUTTONS
// =========================================================

function setupModalCloseButtons() {
    const closeBtn = document.getElementById("closeModal");
    if (closeBtn) closeBtn.addEventListener("click", closeCustomerModal);

    const customerModal = document.getElementById("customerModal");
    if (customerModal) {
        customerModal.addEventListener("click", function (e) {
            if (e.target === customerModal) closeCustomerModal();
        });
    }

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeCustomerModal();
            closeCallModal();
            closeSmsModal();
            closeHistoryModal();
            closeLoanConfirmModal();
        }
    });
}

// =========================================================
// SETUP OFFER INPUTS (Live EMI)
// =========================================================

function setupOfferInputs() {
    const inputs = ["offerAmount", "interestRate", "tenure"];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", updateEmiPreview);
            el.addEventListener("change", updateEmiPreview);
        }
    });
}

// =========================================================
// EMI CALCULATION
// =========================================================

function calculateEmi(principal, annualRate, months) {
    const P = parseFloat(principal) || 0;
    const R = parseFloat(annualRate) || 0;
    const N = parseInt(months) || 0;

    if (P <= 0 || R < 0 || N <= 0) {
        return { emi: 0, totalInterest: 0, totalPayment: 0 };
    }

    const r = R / 12 / 100;

    let emi;
    if (r === 0) {
        emi = P / N;
    } else {
        emi = (P * r * Math.pow(1 + r, N)) / (Math.pow(1 + r, N) - 1);
    }

    const totalPayment = emi * N;
    const totalInterest = totalPayment - P;

    return {
        emi: Math.round(emi),
        totalInterest: Math.round(totalInterest),
        totalPayment: Math.round(totalPayment)
    };
}

function updateEmiPreview() {
    const amount = document.getElementById("offerAmount")?.value;
    const rate = document.getElementById("interestRate")?.value;
    const tenure = document.getElementById("tenure")?.value;

    const result = calculateEmi(amount, rate, tenure);

    setText("emiValue", formatBalance(result.emi));
    setText("totalInterest", formatBalance(result.totalInterest));
    setText("totalPayment", formatBalance(result.totalPayment));
}

// =========================================================
// END OF PART 2
// =========================================================
// =========================================================
// PART 3: CALL + SMS + LOAN + HISTORY MODALS
// =========================================================

// =========================================================
// CALL MODAL
// =========================================================

function setupCallModal() {
    const cutBtn = document.getElementById("cutCallBtn");
    if (cutBtn) cutBtn.addEventListener("click", handleCutCall);

    const closeBtn = document.getElementById("closeCallModal");
    if (closeBtn) closeBtn.addEventListener("click", closeCallModal);

    const callModal = document.getElementById("callModal");
    if (callModal) {
        callModal.addEventListener("click", function (e) {
            if (e.target === callModal) closeCallModal();
        });
    }
}

function openCallModal() {
    if (!currentCustomer) return;

    const modal = document.getElementById("callModal");
    if (!modal) return;

    setText("callCustomerName", "Customer: " + (currentCustomer.customer_id || "--"));

    callSeconds = 0;
    setText("callTimer", "00:00");

    modal.classList.add("active");

    if (callTimerInterval) clearInterval(callTimerInterval);
    callTimerInterval = setInterval(function () {
        callSeconds++;
        const mins = String(Math.floor(callSeconds / 60)).padStart(2, "0");
        const secs = String(callSeconds % 60).padStart(2, "0");
        setText("callTimer", `${mins}:${secs}`);
    }, 1000);
}

function closeCallModal() {
    const modal = document.getElementById("callModal");
    if (modal) modal.classList.remove("active");

    if (callTimerInterval) {
        clearInterval(callTimerInterval);
        callTimerInterval = null;
    }
}

async function handleCutCall() {
    if (callTimerInterval) {
        clearInterval(callTimerInterval);
        callTimerInterval = null;
    }

    const duration = callSeconds;
    const customer = currentCustomer;

    if (!customer) {
        closeCallModal();
        return;
    }

    const customerId = customer.customer_id;

    try {
        const response = await fetch("/api/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_id: customerId,
                action_type: "call",
                channel: "Call",
                message: `Call duration: ${duration} seconds`
            })
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error || "Failed");

        showToast(`📞 Call ended (${duration}s). Record saved!`, "success");

    } catch (err) {
        console.error(err);
        showToast("Call ended, but could not save.", "warning");
    }

    closeCallModal();
    callSeconds = 0;
}

// =========================================================
// SMS MODAL
// =========================================================

function setupSmsModal() {
    const closeBtn = document.getElementById("closeSmsModal");
    if (closeBtn) closeBtn.addEventListener("click", closeSmsModal);

    const smsModal = document.getElementById("smsModal");
    if (smsModal) {
        smsModal.addEventListener("click", function (e) {
            if (e.target === smsModal) closeSmsModal();
        });
    }

    document.querySelectorAll(".sms-message-option").forEach(function (opt) {
        opt.addEventListener("click", function () {
            document.querySelectorAll(".sms-message-option").forEach(o => o.classList.remove("selected"));
            this.classList.add("selected");

            const preview = document.getElementById("smsMessagePreview");
            if (preview) preview.value = this.textContent.trim();
        });
    });

    const sendBtn = document.getElementById("sendSmsBtn");
    if (sendBtn) sendBtn.addEventListener("click", handleSendSms);
}

// =========================================================
// SMS MODAL (Class-Based Templates)
// =========================================================

function getSmsTemplatesByClass(cls) {
    if (cls === "HIGH") {
        return [
            {
                icon: "💎",
                title: "Wealth Management",
                text: "Dear Customer, unlock exclusive Wealth Management services. Personal Relationship Manager, Portfolio Management Services (PMS), and customized investment strategies await you. Book a free consultation today."
            },
            {
                icon: "💳",
                title: "Super-Premium Card",
                text: "Get the HDFC Infinia / SBI Aurum credit card — Unlimited airport lounge access, complimentary golf sessions, luxury hotel privileges, and 24x7 global concierge. Apply now!"
            },
            {
                icon: "🔐",
                title: "Free Locker Facility",
                text: "Enjoy 100% waiver on locker charges or up to 75% discount. Safe, secure, and exclusive for our HNI customers. Visit your branch to avail."
            },
            {
                icon: "💱",
                title: "Zero Forex Markup",
                text: "Zero forex markup on international transactions + lowest borrowing rates on multi-crore loans. Experience truly global banking with SmartLoan."
            },
            {
                icon: "🏨",
                title: "Luxury Lifestyle Offer",
                text: "Complimentary stays at luxury hotels worldwide, heavy dining discounts, and premium concierge service. Live the life you deserve."
            }
        ];
    } else if (cls === "MEDIUM") {
        return [
            {
                icon: "💼",
                title: "Privilege Salary Account",
                text: "Zero-balance salary account with free unlimited ATM withdrawals, complimentary checkbook, and personal accident insurance coverage. Open yours today!"
            },
            {
                icon: "💰",
                title: "Pre-Approved Loan",
                text: "Congratulations! Based on your CIBIL score and transaction history, you're pre-approved for an instant personal/car/home loan. No documents needed. Apply now!"
            },
            {
                icon: "🛍️",
                title: "Shopping Credit Card",
                text: "Get up to 5% flat cashback on online shopping, No-Cost EMI on electronics, and 4-8 free domestic lounge visits/year with our co-branded credit cards."
            },
            {
                icon: "📊",
                title: "Tax-Saving Investments",
                text: "Save tax with SIP, PPF, NPS, and tax-saving FDs. Start with just ₹500/month and grow your wealth while lowering your tax liability."
            },
            {
                icon: "🎉",
                title: "Festive Offer",
                text: "Festive season special! Zero processing fees on home and auto loans + discounted interest rates. Limited period offer. Apply today!"
            }
        ];
    } else {
        // LOW class
        return [
            {
                icon: "🏦",
                title: "PMJDY Zero Balance Account",
                text: "Open a Pradhan Mantri Jan Dhan Yojana account with ZERO minimum balance. Free RuPay debit card + ₹2 lakh accident insurance cover + overdraft up to ₹10,000."
            },
            {
                icon: "🚀",
                title: "Mudra Loan (Business)",
                text: "Start your own shop or business with collateral-free Mudra Loan from ₹50,000 up to ₹10 lakh. Quick approval. Apply at your nearest branch."
            },
            {
                icon: "🛒",
                title: "PM SVANidhi Scheme",
                text: "Street vendors & micro-traders — get collateral-free working capital loans from ₹10,000 to ₹50,000 with easy repayment. Apply now!"
            },
            {
                icon: "🛡️",
                title: "PMJJBY & PMSBY Insurance",
                text: "Get ₹2 lakh life insurance for just ₹436/year and ₹2 lakh accident insurance for just ₹20/year. Enroll through your bank account today."
            },
            {
                icon: "💵",
                title: "Micro Savings Plan",
                text: "Start a Fixed Deposit (FD) or Recurring Deposit (RD) with as low as ₹100 per month. Small savings, big future."
            }
        ];
    }
}

function openSmsModal() {
    if (!currentCustomer) {
        showToast("Please select a customer first.", "error");
        return;
    }

    const modal = document.getElementById("smsModal");
    const list = document.getElementById("smsMessageList");
    if (!modal || !list) return;

    // Get customer's class
    const cls = getCustomerClass(currentCustomer);

    // Get templates based on class
    const templates = getSmsTemplatesByClass(cls);

    // Build template HTML
    list.innerHTML = templates.map((t, index) => `
        <div class="sms-message-option" data-message="template-${index}" data-text="${t.text.replace(/"/g, '&quot;')}">
            <strong>${t.icon} ${t.title}</strong>
            ${t.text}
        </div>
    `).join("");

    // Attach click handlers to new options
    list.querySelectorAll(".sms-message-option").forEach(function (opt) {
        opt.addEventListener("click", function () {
            list.querySelectorAll(".sms-message-option").forEach(o => o.classList.remove("selected"));
            this.classList.add("selected");

            const preview = document.getElementById("smsMessagePreview");
            if (preview) preview.value = this.getAttribute("data-text") || this.textContent.trim();
        });
    });

    // Reset preview
    const preview = document.getElementById("smsMessagePreview");
    if (preview) preview.value = "";

    // Show class label
    const header = modal.querySelector(".modal-header h2");
    if (header) {
        header.textContent = `💬 Send SMS — ${cls} CLASS`;
    }

    modal.classList.add("active");
}

function closeSmsModal() {
    const modal = document.getElementById("smsModal");
    if (modal) modal.classList.remove("active");
}

async function handleSendSms() {
    if (!currentCustomer) {
        showToast("No customer selected.", "error");
        return;
    }

    const preview = document.getElementById("smsMessagePreview");
    const message = preview ? preview.value.trim() : "";

    if (!message) {
        showToast("Please select a message template.", "warning");
        return;
    }

    const customerId = currentCustomer.customer_id;

    try {
        const response = await fetch("/api/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_id: customerId,
                action_type: "sms",
                channel: "SMS",
                message: message
            })
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error || "Failed");

        showToast("💬 SMS sent and recorded!", "success");
        closeSmsModal();

    } catch (err) {
        console.error(err);
        showToast("Could not send SMS.", "error");
    }
}

// =========================================================
// LOAN CONFIRM MODAL
// =========================================================

function setupLoanConfirmModal() {
    const confirmBtn = document.getElementById("confirmLoanBtn");
    if (confirmBtn) confirmBtn.addEventListener("click", handleConfirmLoan);

    const cancelBtn = document.getElementById("cancelLoanBtn");
    if (cancelBtn) cancelBtn.addEventListener("click", closeLoanConfirmModal);

    const closeBtn = document.getElementById("closeLoanModal");
    if (closeBtn) closeBtn.addEventListener("click", closeLoanConfirmModal);

    const loanModal = document.getElementById("loanConfirmModal");
    if (loanModal) {
        loanModal.addEventListener("click", function (e) {
            if (e.target === loanModal) closeLoanConfirmModal();
        });
    }

    const loanBtn = document.getElementById("loanBtn");
    if (loanBtn) loanBtn.addEventListener("click", openLoanConfirmModal);
}

function openLoanConfirmModal() {
    if (!currentCustomer) {
        showToast("Please select a customer first.", "error");
        return;
    }

    const amount = parseFloat(document.getElementById("offerAmount")?.value) || 0;
    const rate = parseFloat(document.getElementById("interestRate")?.value) || 0;
    const tenure = parseInt(document.getElementById("tenure")?.value) || 0;

    if (amount <= 0 || rate <= 0 || tenure <= 0) {
        showToast("Please fill all loan details.", "warning");
        return;
    }

    const emi = calculateEmi(amount, rate, tenure);

    setText("loanCustomerName", currentCustomer.customer_id || "--");
    setText("loanAmountDisplay", formatBalance(amount));
    setText("loanRateDisplay", rate + "%");
    setText("loanTenureDisplay", tenure + " Months");
    setText("loanEmiDisplay", formatBalance(emi.emi));
    setText("loanTotalDisplay", formatBalance(emi.totalPayment));

    const modal = document.getElementById("loanConfirmModal");
    if (modal) modal.classList.add("active");
}

function closeLoanConfirmModal() {
    const modal = document.getElementById("loanConfirmModal");
    if (modal) modal.classList.remove("active");
}

async function handleConfirmLoan() {
    if (!currentCustomer) return;

    const amount = parseFloat(document.getElementById("offerAmount")?.value) || 0;
    const rate = parseFloat(document.getElementById("interestRate")?.value) || 0;
    const tenure = parseInt(document.getElementById("tenure")?.value) || 0;

    const customerId = currentCustomer.customer_id;

    try {
        const response = await fetch("/api/create-offer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_id: customerId,
                offer_type: "Personal Loan",
                amount: amount,
                interest_rate: rate,
                tenure: tenure,
                channel: "App"
            })
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error || "Failed");

        showToast(`💰 Loan offer created! EMI: ${formatBalance(result.emi_details?.emi || 0)}`, "success");

        closeLoanConfirmModal();
        closeCustomerModal();

    } catch (err) {
        console.error(err);
        showToast("Could not create loan offer.", "error");
    }
}

// =========================================================
// HISTORY MODAL
// =========================================================

function setupHistoryModal() {
    const closeBtn = document.getElementById("closeHistoryModal");
    if (closeBtn) closeBtn.addEventListener("click", closeHistoryModal);

    const historyModal = document.getElementById("historyModal");
    if (historyModal) {
        historyModal.addEventListener("click", function (e) {
            if (e.target === historyModal) closeHistoryModal();
        });
    }

    const histBtn = document.getElementById("historyBtn");
    if (histBtn) histBtn.addEventListener("click", openHistoryModal);

    document.querySelectorAll(".history-tab").forEach(function (tab) {
        tab.addEventListener("click", function () {
            document.querySelectorAll(".history-tab").forEach(t => t.classList.remove("active"));
            this.classList.add("active");
            const tabName = this.getAttribute("data-tab");
            filterHistory(tabName);
        });
    });
}

async function openHistoryModal() {
    if (!currentCustomer) {
        showToast("Please select a customer first.", "error");
        return;
    }

    const modal = document.getElementById("historyModal");
    if (!modal) return;

    setText("historyCustomerName", "Customer: " + currentCustomer.customer_id);

    const list = document.getElementById("historyList");
    if (list) list.innerHTML = `<div class="empty">Loading history...</div>`;

    modal.classList.add("active");

    const customerId = currentCustomer.customer_id;

    try {
        const response = await fetch(`/api/customer-history/${customerId}`);
        const data = await response.json();

        if (!data.success) throw new Error(data.error || "Failed");

        currentHistoryData = {
            actions: data.actions || [],
            offers: data.offers || []
        };

        filterHistory("all");

    } catch (err) {
        console.error(err);
        if (list) list.innerHTML = `<div class="empty">No history found.</div>`;
    }
}

function closeHistoryModal() {
    const modal = document.getElementById("historyModal");
    if (modal) modal.classList.remove("active");
}

function filterHistory(tab) {
    const list = document.getElementById("historyList");
    if (!list) return;

    const history = currentHistoryData;
    let items = [];

    if (tab === "all" || tab === "call" || tab === "sms") {
        history.actions.forEach(a => {
            if (tab === "all" || a.action_type === tab) {
                items.push({
                    type: a.action_type,
                    channel: a.channel,
                    message: a.message,
                    status: a.status,
                    created_at: a.created_at
                });
            }
        });
    }

    if (tab === "all" || tab === "loan") {
        history.offers.forEach(o => {
            items.push({
                type: "loan",
                channel: o.channel,
                message: `${o.offer_type} — ₹${o.amount} at ${o.interest_rate}% for ${o.tenure} months`,
                status: o.status,
                created_at: o.created_at
            });
        });
    }

    if (items.length === 0) {
        list.innerHTML = `<div class="empty">No ${tab} history found.</div>`;
        return;
    }

    list.innerHTML = items.map(item => {
        const icon = item.type === "call" ? "📞" : item.type === "sms" ? "💬" : "💰";
        return `
            <div class="history-item">
                <div class="history-item-header">
                    <span class="history-item-type">${icon} ${item.type.toUpperCase()} — ${item.channel || ""}</span>
                    <span class="history-item-time">${item.created_at || ""}</span>
                </div>
                <div class="history-item-body">${item.message || ""}</div>
                <div class="history-item-time" style="margin-top: 6px;">
                    Status: ${item.status || "Completed"}
                </div>
            </div>
        `;
    }).join("");
}

// =========================================================
// END OF PART 3
// =========================================================
// =========================================================
// PART 4: TOAST + CHARTS + GLOBAL HANDLERS
// =========================================================

// =========================================================
// TOAST NOTIFICATIONS
// =========================================================

function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast " + type;

    const icons = {
        success: "✅",
        error: "❌",
        warning: "⚠️",
        info: "ℹ️"
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || "ℹ️"}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(function () {
        toast.classList.add("hide");
        setTimeout(function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 300);
    }, 4000);
}

// =========================================================
// CHARTS (Analytics)
// =========================================================

function renderCharts(stats) {
    // Pie / Doughnut Chart
    const pieCanvas = document.getElementById("pieChart");
    if (pieCanvas) {
        if (pieChartInstance) pieChartInstance.destroy();

        pieChartInstance = new Chart(pieCanvas, {
            type: "doughnut",
            data: {
                labels: ["LOW", "MEDIUM", "HIGH"],
                datasets: [{
                    data: [stats.LOW || 0, stats.MEDIUM || 0, stats.HIGH || 0],
                    backgroundColor: ["#22c55e", "#f2ad3d", "#3b82f6"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#b8c2d0", font: { size: 12 } }
                    }
                }
            }
        });
    }

    // Bar Chart
    const barCanvas = document.getElementById("barChart");
    if (barCanvas) {
        if (barChartInstance) barChartInstance.destroy();

        barChartInstance = new Chart(barCanvas, {
            type: "bar",
            data: {
                labels: ["LOW", "MEDIUM", "HIGH"],
                datasets: [{
                    label: "Customers",
                    data: [stats.LOW || 0, stats.MEDIUM || 0, stats.HIGH || 0],
                    backgroundColor: ["#22c55e", "#f2ad3d", "#3b82f6"],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: "#8d99aa" },
                        grid: { color: "rgba(255,255,255,0.05)" }
                    },
                    x: {
                        ticks: { color: "#8d99aa" },
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

// =========================================================
// GLOBAL CLICK HANDLERS (Buttons that need currentCustomer)
// =========================================================

function setupGlobalClickHandlers() {
    // Call Button
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "callBtn") {
            if (!currentCustomer) {
                showToast("Please select a customer first.", "error");
                return;
            }
            openCallModal();
        }
    });

    // SMS Button
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "smsBtn") {
            openSmsModal();
        }
    });
}

// =========================================================
// WINDOW LOAD — Initial State
// =========================================================

window.addEventListener("load", function () {
    console.log("✅ All scripts loaded — SmartLoan Trigger ready!");

    // Dashboard band rakho, login screen dikhao
    const dashboard = document.getElementById("dashboard");
    const loginScreen = document.getElementById("login-screen");
    const customerModal = document.getElementById("customerModal");

    if (dashboard) dashboard.style.display = "none";
    if (loginScreen) loginScreen.style.display = "flex";
    if (customerModal) customerModal.classList.remove("active");
});

// =========================================================
// END OF APP.JS
// =========================================================

console.log("✅ SmartLoan Trigger app_v3.js fully loaded!");