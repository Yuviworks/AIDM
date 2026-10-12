(function () {
    const message = document.getElementById("maintenanceProposalMessage");
    const list = document.getElementById("maintenanceProposals");
    const refreshButton = document.getElementById("refreshMaintenanceProposals");
    const scanButton = document.getElementById("scanMaintenanceProposals");

    function setMessage(text, kind) {
        if (!message) return;
        message.className = kind ? "alert alert-" + kind : "mb-3";
        message.textContent = text || "";
    }

    function escapeText(value) {
        return String(value ?? "").replace(/[&<>"']/g, function (char) {
            return ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"})[char];
        });
    }

    async function request(url, options) {
        const response = await fetch(url, options || {});
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || "Request failed");
        return data;
    }

    function render(proposals) {
        if (!list) return;
        if (!proposals.length) {
            list.innerHTML = '<div class="history-empty">No proposals yet. Use “Check maintenance now” to run a scan. Proposals are created only when maintenance is due within the reminder window and a demo slot exists.</div>';
            return;
        }
        list.innerHTML = proposals.map(function (p) {
            const pending = p.status === "PENDING";
            const statusClass = p.status === "CONFIRMED" ? "success" : (p.status === "PENDING" ? "warning" : "secondary");
            return '<article class="border rounded-3 p-3 mb-3">' +
                '<div class="d-flex flex-wrap justify-content-between gap-2"><h3 class="h5 mb-1">' + escapeText(p.appliance_model) + '</h3>' +
                '<span class="badge text-bg-' + statusClass + '">' + escapeText(p.status) + '</span></div>' +
                '<p class="mb-1">Maintenance due: <strong>' + escapeText(p.maintenance_due_date) + '</strong></p>' +
                '<p class="mb-1">Suggested appointment: <strong>' + escapeText(p.proposed_slot) + '</strong></p>' +
                '<p class="mb-2">Demo provider: ' + escapeText(p.service_center_name) + (p.service_center_location ? ' — ' + escapeText(p.service_center_location) : '') + '</p>' +
                (pending ? '<div class="d-flex gap-2 flex-wrap"><button type="button" class="btn btn-success" data-proposal-id="' + Number(p.id) + '" data-decision="confirm">Yes, confirm appointment</button><button type="button" class="btn btn-outline-secondary" data-proposal-id="' + Number(p.id) + '" data-decision="decline">No, not now</button></div>' : '') +
                (p.booking_id ? '<p class="mt-2 mb-0">AIDM booking reference: #' + Number(p.booking_id) + '</p>' : '') +
                '</article>';
        }).join("");
    }

    async function loadProposals() {
        if (!userId || !list) return;
        try {
            const data = await request(API_URL + "/maintenance-proposals/user/" + encodeURIComponent(userId));
            render(data);
        } catch (error) {
            setMessage(error.message, "danger");
            list.innerHTML = "";
        }
    }

    async function scanNow() {
        scanButton.disabled = true;
        setMessage("Checking appliance schedules…");
        try {
            const result = await request(API_URL + "/maintenance-proposals/scan", {method:"POST"});
            setMessage("Scan complete. Checked " + result.checked + " appliance(s); created " + result.created + " new proposal(s). Reminder window: " + result.reminder_window_days + " day(s).", "info");
            await loadProposals();
        } catch (error) {
            setMessage(error.message, "danger");
        } finally {
            scanButton.disabled = false;
        }
    }

    if (refreshButton) refreshButton.addEventListener("click", loadProposals);
    if (scanButton) scanButton.addEventListener("click", scanNow);
    if (list) list.addEventListener("click", async function (event) {
        const button = event.target.closest("button[data-proposal-id]");
        if (!button) return;
        const proposalId = button.getAttribute("data-proposal-id");
        const decision = button.getAttribute("data-decision");
        button.disabled = true;
        try {
            const result = await request(API_URL + "/maintenance-proposals/" + proposalId + "/respond?user_id=" + encodeURIComponent(userId) + "&decision=" + encodeURIComponent(decision), {method:"POST"});
            setMessage(result.message + (result.provider_notice ? " " + result.provider_notice : ""), decision === "confirm" ? "success" : "secondary");
            await loadProposals();
            if (typeof loadBookingHistory === "function") await loadBookingHistory();
        } catch (error) {
            setMessage(error.message, "danger");
            button.disabled = false;
        }
    });

    loadProposals();
})();