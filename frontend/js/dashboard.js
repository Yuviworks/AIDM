const API_URL = "http://127.0.0.1:8000";

const userId = localStorage.getItem("user_id");
const userName = localStorage.getItem("user_name");

let appliances = [];
let appliance = null;

let agentServiceCenters = [];
let selectedAgentCenter = null;
let selectedAgentSlot = null;

if (!userId) {
    window.location.href = "index.html";
}


/* =========================================================
   WELCOME USER
   ========================================================= */

const welcomeUser = document.getElementById("welcomeUser");

if (welcomeUser) {
    welcomeUser.textContent =
        `Welcome, ${userName || "User"}`;
}


/* =========================================================
   LOGOUT
   ========================================================= */

const logoutButton =
    document.getElementById("logoutButton");

if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        function () {

            localStorage.clear();

            window.location.href =
                "index.html";
        }
    );
}


/* =========================================================
   HELPER FUNCTIONS
   ========================================================= */

function escapeHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function getApplianceIcon(type) {

    const value =
        String(type || "").toLowerCase();

    if (
        value.includes("water") ||
        value.includes("purifier")
    ) {
        return "bi-droplet-half";
    }

    if (value.includes("air")) {
        return "bi-snow";
    }

    if (value.includes("washing")) {
        return "bi-water";
    }

    if (value.includes("refrigerator")) {
        return "bi-box";
    }

    return "bi-cpu";
}


/* =========================================================
   UPDATE APPLIANCE OVERVIEW
   ========================================================= */

function updateApplianceOverview() {

    if (!appliance) {
        return;
    }

    const applianceType =
        document.getElementById("applianceType");

    const applianceBrand =
        document.getElementById("applianceBrand");

    const applianceModel =
        document.getElementById("applianceModel");

    const lastService =
        document.getElementById("lastService");


    if (applianceType) {

        applianceType.textContent =
            appliance.appliance_type;
    }


    if (applianceBrand) {

        applianceBrand.textContent =
            appliance.brand;
    }


    if (applianceModel) {

        applianceModel.textContent =
            appliance.model;
    }


    if (lastService) {

        lastService.textContent =
            appliance.last_service_date;
    }


    const icon =
        document.querySelector(
            ".appliance-main-icon i"
        );


    if (icon) {

        icon.className =
            `bi ${getApplianceIcon(
                appliance.appliance_type
            )}`;
    }
}


/* =========================================================
   ASK AIDM — MODEL-SPECIFIC RAG
   ========================================================= */

function updateAskAIDMModel() {

    const modelElement =
        document.getElementById("askAIDMModel");

    if (!modelElement) {
        return;
    }

    if (!appliance) {

        modelElement.textContent =
            "No purifier selected";

        return;
    }

    modelElement.textContent =
        `${appliance.brand} ${appliance.model}`;
}


/* =========================================================
   RESET ASK AIDM
   ========================================================= */

function resetAskAIDM() {

    const questionInput =
        document.getElementById("aidmQuestion");

    const result =
        document.getElementById("aidmQuestionResult");

    const answer =
        document.getElementById("aidmQuestionAnswer");

    const source =
        document.getElementById("aidmQuestionSource");

    const button =
        document.getElementById("askAIDMButton");


    if (questionInput) {
        questionInput.value = "";
    }


    if (result) {
        result.style.display = "none";
    }


    if (answer) {
        answer.innerHTML = "";
    }


    if (source) {
        source.textContent = "";
    }


    if (button) {

        button.disabled = false;

        button.innerHTML =
            "🤖 Ask AIDM";
    }


    updateAskAIDMModel();
}


/* =========================================================
   FORMAT AI RESPONSE
   ========================================================= */

function formatAIResponse(text) {

    return escapeHtml(text)
        .replace(/\n/g, "<br>");
}


/* =========================================================
   ASK AIDM
   ========================================================= */

async function askAIDM() {

    if (!appliance) {

        alert(
            "Please select a purifier first."
        );

        return;
    }


    const questionInput =
        document.getElementById("aidmQuestion");

    const button =
        document.getElementById("askAIDMButton");

    const result =
        document.getElementById("aidmQuestionResult");

    const answer =
        document.getElementById("aidmQuestionAnswer");

    const source =
        document.getElementById("aidmQuestionSource");


    if (!questionInput) {
        return;
    }


    const question =
        questionInput.value.trim();


    if (!question) {

        alert(
            "Please enter a question."
        );

        questionInput.focus();

        return;
    }


    /*
       Store the appliance/model used for this request.
       This prevents an old response from being displayed
       if the user changes the selected appliance while
       the RAG request is running.
    */

    const requestedApplianceId =
        Number(appliance.id);

    const requestedModel =
        appliance.model;


    if (button) {

        button.disabled = true;

        button.innerHTML =
            "⏳ AIDM is thinking...";
    }


    if (result) {
        result.style.display = "block";
    }


    if (answer) {

        answer.innerHTML = `
            <div class="text-muted">

                Searching the
                ${escapeHtml(appliance.brand)}
                ${escapeHtml(appliance.model)}
                maintenance manual...

            </div>
        `;
    }


    if (source) {
        source.textContent = "";
    }


    try {

        const response =
            await fetch(
                `${API_URL}/rag/explain`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        query:
                            question,

                        model:
                            requestedModel
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to get an answer from AIDM."
            );
        }


        /*
           Do not display the answer if the user
           changed the selected appliance while
           the request was running.
        */

        if (
            !appliance ||
            Number(appliance.id) !==
                requestedApplianceId
        ) {

            return;
        }


        if (answer) {

            answer.innerHTML =
                formatAIResponse(
                    data.answer ||
                    "No answer was returned."
                );
        }


        if (source) {

            source.textContent =
                `Answer generated from the ${requestedModel} maintenance manual.`;
        }


    } catch (error) {

        console.error(
            "Ask AIDM Error:",
            error
        );


        if (answer) {

            answer.innerHTML = `
                <div class="alert alert-danger mb-0">

                    <strong>
                        Unable to get an answer.
                    </strong>

                    <div class="mt-1">

                        ${escapeHtml(
                            error.message
                        )}

                    </div>

                </div>
            `;
        }


        if (source) {
            source.textContent = "";
        }


    } finally {

        if (button) {

            button.disabled = false;

            button.innerHTML =
                "🤖 Ask AIDM";
        }
    }
}


/* =========================================================
   ASK AIDM BUTTON
   ========================================================= */

const askAIDMButton =
    document.getElementById(
        "askAIDMButton"
    );


if (askAIDMButton) {

    askAIDMButton.addEventListener(
        "click",
        askAIDM
    );
}


/* =========================================================
   ASK AIDM CTRL + ENTER
   ========================================================= */

const aidmQuestion =
    document.getElementById(
        "aidmQuestion"
    );


if (aidmQuestion) {

    aidmQuestion.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                (event.ctrlKey || event.metaKey)
            ) {

                event.preventDefault();

                askAIDM();
            }
        }
    );
}


/* =========================================================
   RESET AI AGENT UI
   ========================================================= */

function resetAgentUI() {

    agentServiceCenters = [];

    selectedAgentCenter = null;

    selectedAgentSlot = null;


    const agentResults =
        document.getElementById(
            "agentResults"
        );

    const agentConfirmation =
        document.getElementById(
            "agentConfirmation"
        );

    const agentBookingResult =
        document.getElementById(
            "agentBookingResult"
        );

    const agentExplanation =
        document.getElementById(
            "agentExplanation"
        );

    const centerSelect =
        document.getElementById(
            "agentServiceCenterSelect"
        );

    const slotSelect =
        document.getElementById(
            "agentSlotSelect"
        );

    const distance =
        document.getElementById(
            "agentServiceDistance"
        );

    const status =
        document.getElementById(
            "agentStatus"
        );


    if (agentResults) {

        agentResults.style.display =
            "none";
    }


    if (agentConfirmation) {

        agentConfirmation.style.display =
            "none";
    }


    if (agentBookingResult) {

        agentBookingResult.style.display =
            "none";

        agentBookingResult.innerHTML =
            "";
    }


    if (agentExplanation) {

        agentExplanation.textContent =
            "-";
    }


    if (centerSelect) {

        centerSelect.innerHTML = `
            <option value="">
                Select service center
            </option>
        `;

        centerSelect.value = "";
    }


    if (slotSelect) {

        slotSelect.innerHTML = `
            <option value="">
                Select service slot
            </option>
        `;

        slotSelect.disabled = true;

        slotSelect.value = "";
    }


    if (distance) {

        distance.textContent = "";
    }


    if (status) {

        status.innerHTML = `
            <div class="agent-status-inner">

                <div class="agent-status-icon">

                    <i class="bi bi-stars"></i>

                </div>

                <div>

                    <strong>
                        Agent ready
                    </strong>

                    <p>
                        Click "Run AI Agent" to analyze your selected appliance.
                    </p>

                </div>

            </div>
        `;
    }


    window.aidmRecommendation = null;
}


/* =========================================================
   SELECT APPLIANCE
   ========================================================= */

async function selectAppliance(
    selectedId,
    saveSelection = true
) {

    const selected =
        appliances.find(
            item =>
                Number(item.id) ===
                Number(selectedId)
        );


    if (!selected) {
        return;
    }


    appliance = selected;


    if (saveSelection) {

        localStorage.setItem(
            "selected_appliance",
            appliance.id
        );
    }


    renderApplianceList();

    updateApplianceOverview();

    updateAskAIDMModel();

    resetAskAIDM();

    resetAgentUI();

    await loadMaintenance();

    await loadServiceCenters();
}


/* =========================================================
   LOAD ALL APPLIANCES
   ========================================================= */

async function loadAppliances() {

    try {

        const response =
            await fetch(
                `${API_URL}/appliances/user/${userId}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load appliances"
            );
        }


        appliances =
            Array.isArray(data)
                ? data
                : [];


        const loadingMessage =
            document.getElementById(
                "loadingMessage"
            );


        if (loadingMessage) {

            loadingMessage.style.display =
                "none";
        }


        /* No appliances */

        if (appliances.length === 0) {

            appliance = null;

            localStorage.removeItem(
                "selected_appliance"
            );

            updateAskAIDMModel();

            resetAskAIDM();


            const registerSection =
                document.getElementById(
                    "registerApplianceSection"
                );

            const dashboardContent =
                document.getElementById(
                    "dashboardContent"
                );

            const appliancesSection =
                document.getElementById(
                    "appliancesSection"
                );


            if (registerSection) {

                registerSection.style.display =
                    "block";
            }


            if (dashboardContent) {

                dashboardContent.style.display =
                    "none";
            }


            if (appliancesSection) {

                appliancesSection.style.display =
                    "none";
            }


            return;
        }


        /* Restore previously selected appliance */

        const savedId =
            Number(
                localStorage.getItem(
                    "selected_appliance"
                )
            );


        const savedAppliance =
            appliances.find(
                item =>
                    Number(item.id) ===
                    savedId
            );


        appliance =
            savedAppliance ||
            appliances[0];


        localStorage.setItem(
            "selected_appliance",
            appliance.id
        );


        const registerSection =
            document.getElementById(
                "registerApplianceSection"
            );

        const dashboardContent =
            document.getElementById(
                "dashboardContent"
            );

        const appliancesSection =
            document.getElementById(
                "appliancesSection"
            );


        if (registerSection) {

            registerSection.style.display =
                "none";
        }


        if (dashboardContent) {

            dashboardContent.style.display =
                "block";
        }


        if (appliancesSection) {

            appliancesSection.style.display =
                "block";
        }


        renderApplianceList();

        updateApplianceOverview();

        updateAskAIDMModel();

        resetAskAIDM();

        await loadMaintenance();

        await loadServiceCenters();


    } catch (error) {

        console.error(
            "Load Appliances Error:",
            error
        );


        const loadingMessage =
            document.getElementById(
                "loadingMessage"
            );


        if (loadingMessage) {

            loadingMessage.className =
                "alert alert-danger";

            loadingMessage.textContent =
                "Unable to load appliance information.";
        }
    }
}


/* =========================================================
   RENDER APPLIANCE LIST
   ========================================================= */

function renderApplianceList() {

    const container =
        document.getElementById(
            "applianceList"
        );


    if (!container) {
        return;
    }


    if (appliances.length === 0) {

        container.innerHTML = "";

        return;
    }


    container.innerHTML = "";


    appliances.forEach(
        item => {

            const isSelected =
                appliance &&
                Number(item.id) ===
                Number(appliance.id);


            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "col-md-6 col-lg-4";


            card.innerHTML = `

                <div
                    class="aidm-card h-100"
                    style="
                        cursor: pointer;
                        transition: 0.2s ease;
                        ${
                            isSelected
                                ? "border: 2px solid #0d6efd;"
                                : ""
                        }
                    "
                >

                    <div class="d-flex justify-content-between align-items-start">

                        <div class="d-flex align-items-center gap-3">

                            <div class="section-icon">

                                <i class="bi ${getApplianceIcon(
                                    item.appliance_type
                                )}"></i>

                            </div>


                            <div>

                                <div class="small-label">

                                    ${
                                        isSelected
                                            ? "SELECTED"
                                            : "REGISTERED APPLIANCE"
                                    }

                                </div>


                                <h4 class="mb-1">

                                    ${escapeHtml(
                                        item.model
                                    )}

                                </h4>


                                <p class="mb-0 text-muted">

                                    ${escapeHtml(
                                        item.brand
                                    )}

                                </p>

                            </div>

                        </div>


                        ${
                            isSelected
                                ? `
                                    <span class="badge bg-primary">
                                        Active
                                    </span>
                                `
                                : ""
                        }

                    </div>


                    <div class="mt-3 pt-3 border-top">

                        <div class="d-flex justify-content-between mb-2">

                            <span class="text-muted">
                                Type
                            </span>

                            <strong>

                                ${escapeHtml(
                                    item.appliance_type
                                )}

                            </strong>

                        </div>


                        <div class="d-flex justify-content-between mb-3">

                            <span class="text-muted">
                                Last Service
                            </span>

                            <strong>

                                ${escapeHtml(
                                    item.last_service_date
                                )}

                            </strong>

                        </div>


                        <div class="d-flex gap-2">

                            <button
                                type="button"
                                class="btn ${
                                    isSelected
                                        ? "btn-primary"
                                        : "btn-outline-primary"
                                } flex-grow-1 appliance-select-button"
                                data-appliance-id="${item.id}"
                            >

                                ${
                                    isSelected
                                        ? "Currently Selected"
                                        : "View Dashboard"
                                }

                            </button>


                            <button
                                type="button"
                                class="btn btn-outline-danger remove-appliance-button"
                                data-appliance-id="${item.id}"
                                title="Remove appliance"
                            >

                                <i class="bi bi-trash"></i>

                            </button>

                        </div>

                    </div>

                </div>

            `;


            const button =
                card.querySelector(
                    ".appliance-select-button"
                );


            if (button) {

                button.addEventListener(
                    "click",
                    async function () {

                        await selectAppliance(
                            item.id
                        );


                        const dashboardContent =
                            document.getElementById(
                                "dashboardContent"
                            );


                        if (dashboardContent) {

                            dashboardContent.scrollIntoView({
                                behavior: "smooth",
                                block: "start"
                            });
                        }
                    }
                );
            }


            /* REMOVE APPLIANCE BUTTON */

            const removeButton =
                card.querySelector(
                    ".remove-appliance-button"
                );


            if (removeButton) {

                removeButton.addEventListener(
                    "click",
                    async function (event) {

                        event.stopPropagation();

                        await removeAppliance(
                            item.id
                        );
                    }
                );
            }


            container.appendChild(
                card
            );
        }
    );
}


/* =========================================================
   REMOVE APPLIANCE
   ========================================================= */

async function removeAppliance(
    applianceId
) {

    const selected =
        appliances.find(
            item =>
                Number(item.id) ===
                Number(applianceId)
        );


    if (!selected) {
        return;
    }


    const confirmed =
        confirm(
            `Are you sure you want to remove ${selected.model}?\n\n` +
            `This will also remove its service history and bookings.`
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/appliances/${applianceId}` +
                `?user_id=${encodeURIComponent(userId)}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to remove appliance."
            );
        }


        /* Remove from local array */

        appliances =
            appliances.filter(
                item =>
                    Number(item.id) !==
                    Number(applianceId)
            );


        /* Remove selected appliance */

        if (
            appliance &&
            Number(appliance.id) ===
            Number(applianceId)
        ) {

            appliance = null;

            localStorage.removeItem(
                "selected_appliance"
            );

            updateAskAIDMModel();

            resetAskAIDM();
        }


        resetAgentUI();

        renderApplianceList();


        /* Reload service history */

        await loadBookingHistory();


        /* If no appliances remain */

        if (appliances.length === 0) {

            const dashboardContent =
                document.getElementById(
                    "dashboardContent"
                );

            const appliancesSection =
                document.getElementById(
                    "appliancesSection"
                );

            const registerSection =
                document.getElementById(
                    "registerApplianceSection"
                );


            if (dashboardContent) {

                dashboardContent.style.display =
                    "none";
            }


            if (appliancesSection) {

                appliancesSection.style.display =
                    "none";
            }


            if (registerSection) {

                registerSection.style.display =
                    "block";
            }


            const serviceCenters =
                document.getElementById(
                    "serviceCenters"
                );


            if (serviceCenters) {

                serviceCenters.innerHTML =
                    "";
            }


            alert(
                `${selected.model} was removed successfully.`
            );


            return;
        }


        /* Select another remaining appliance */

        await selectAppliance(
            appliances[0].id,
            true
        );


        alert(
            `${selected.model} was removed successfully.`
        );


    } catch (error) {

        console.error(
            "Remove Appliance Error:",
            error
        );


        alert(
            `Unable to remove appliance.\n\n${error.message}`
        );
    }
}


/* =========================================================
   MAINTENANCE
   ========================================================= */

async function loadMaintenance() {

    if (!appliance) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/maintenance/${appliance.id}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Maintenance check failed"
            );
        }


        const statusElement =
            document.getElementById(
                "maintenanceStatus"
            );


        if (statusElement) {

            if (
                data.status ===
                "MAINTENANCE_DUE"
            ) {

                statusElement.className =
                    "maintenance-status maintenance-due";

                statusElement.textContent =
                    "⚠️ Maintenance Required";

            } else {

                statusElement.className =
                    "maintenance-status maintenance-upcoming";

                statusElement.textContent =
                    "✓ Maintenance is not currently due";
            }
        }


        const nextMaintenance =
            document.getElementById(
                "nextMaintenance"
            );


        if (nextMaintenance) {

            nextMaintenance.textContent =
                data.next_maintenance_date;
        }


        const maintenanceInterval =
            document.getElementById(
                "maintenanceInterval"
            );


        if (maintenanceInterval) {

            maintenanceInterval.textContent =
                `${data.maintenance_interval_months} months`;
        }


    } catch (error) {

        console.error(
            "Maintenance Error:",
            error
        );
    }
}


/* =========================================================
   SERVICE CENTERS
   ========================================================= */

async function loadServiceCenters() {

    if (!appliance) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/service/centers` +
                `?brand=${encodeURIComponent(
                    appliance.brand
                )}` +
                `&location=Pune`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load service centers"
            );
        }


        agentServiceCenters =
            data.service_centers || [];


        const container =
            document.getElementById(
                "serviceCenters"
            );


        if (!container) {
            return;
        }


        if (
            agentServiceCenters.length === 0
        ) {

            container.innerHTML = `
                <div class="alert alert-warning">

                    No service centers found.

                </div>
            `;

            return;
        }


        container.innerHTML = "";


        agentServiceCenters.forEach(
            center => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "col-md-4 mb-3";


                card.innerHTML = `

                    <div class="card h-100 border">

                        <div class="card-body">

                            <h6 class="fw-bold">

                                ${escapeHtml(
                                    center.name
                                )}

                            </h6>


                            <p class="mb-1">

                                📍 ${escapeHtml(
                                    center.location
                                )}

                            </p>


                            <p class="mb-1">

                                📞 ${escapeHtml(
                                    center.phone
                                )}

                            </p>


                            <p class="mb-1">

                                📏 ${escapeHtml(
                                    center.distance_km
                                )} km away

                            </p>


                            <p class="text-muted small">

                                🕒 ${escapeHtml(
                                    center.availability
                                )}

                            </p>


                            <button
                                type="button"
                                class="btn btn-primary btn-sm"
                                onclick="openBooking(${center.id})"
                            >

                                Book Service

                            </button>

                        </div>

                    </div>

                `;


                container.appendChild(
                    card
                );
            }
        );


    } catch (error) {

        console.error(
            "Service Center Error:",
            error
        );


        const container =
            document.getElementById(
                "serviceCenters"
            );


        if (container) {

            container.innerHTML = `
                <div class="alert alert-danger">

                    Unable to load service centers.

                </div>
            `;
        }
    }
}


/* =========================================================
   NORMAL BOOKING PAGE
   ========================================================= */

function openBooking(
    serviceCenterId
) {

    if (!appliance) {
        return;
    }


    localStorage.setItem(
        "selected_service_center",
        serviceCenterId
    );


    localStorage.setItem(
        "selected_appliance",
        appliance.id
    );


    window.location.href =
        "booking.html";
}


/* =========================================================
   SERVICE HISTORY
   ========================================================= */

async function loadBookingHistory() {

    try {

        const response =
            await fetch(
                `${API_URL}/booking/user/${userId}`
            );


        const bookings =
            await response.json();


        if (!response.ok) {

            throw new Error(
                bookings.detail ||
                "Unable to load service history"
            );
        }


        const container =
            document.getElementById(
                "bookingHistory"
            );


        if (!container) {
            return;
        }


        if (bookings.length === 0) {

            container.innerHTML = `

                <div class="history-empty">

                    <i class="bi bi-hourglass-split"></i>

                    <span>
                        No service bookings yet.
                    </span>

                </div>

            `;

            return;
        }


        container.innerHTML = "";


        bookings.forEach(
            booking => {

                const bookingAppliance =
                    appliances.find(
                        item =>
                            Number(item.id) ===
                            Number(
                                booking.appliance_id
                            )
                    );


                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "card border mb-3";


                card.innerHTML = `

                    <div class="card-body">

                        <div class="row align-items-center">

                            <div class="col-md-3">

                                <small class="text-muted">
                                    Booking ID
                                </small>

                                <p class="fw-bold mb-0">

                                    #${escapeHtml(
                                        booking.id
                                    )}

                                </p>

                            </div>


                            <div class="col-md-3">

                                <small class="text-muted">
                                    Appliance
                                </small>

                                <p class="fw-bold mb-0">

                                    ${
                                        bookingAppliance
                                            ? escapeHtml(
                                                bookingAppliance.model
                                            )
                                            : `Appliance #${escapeHtml(
                                                booking.appliance_id
                                            )}`
                                    }

                                </p>

                            </div>


                            <div class="col-md-3">

                                <small class="text-muted">
                                    Service Date
                                </small>

                                <p class="fw-bold mb-0">

                                    ${escapeHtml(
                                        booking.booking_date
                                    )}

                                </p>


                                ${
                                    booking.booking_slot
                                        ? `
                                            <small class="text-muted">

                                                🕐 ${escapeHtml(
                                                    booking.booking_slot
                                                )}

                                            </small>
                                        `
                                        : ""
                                }

                            </div>


                            <div class="col-md-3">

                                <small class="text-muted">
                                    Service Center
                                </small>

                                <p class="fw-bold mb-1">

                                    Center #${escapeHtml(
                                        booking.service_center_id
                                    )}

                                </p>


                                <span class="badge bg-success">

                                    ${escapeHtml(
                                        booking.status
                                    )}

                                </span>

                            </div>

                        </div>

                    </div>

                `;


                container.appendChild(
                    card
                );
            }
        );


    } catch (error) {

        console.error(
            "Booking History Error:",
            error
        );
    }
}


/* =========================================================
   AGENT CENTER DROPDOWN
   ========================================================= */

function populateAgentCenterDropdown() {

    const select =
        document.getElementById(
            "agentServiceCenterSelect"
        );


    if (!select) {
        return;
    }


    select.innerHTML = `

        <option value="">
            Select service center
        </option>

    `;


    agentServiceCenters.forEach(
        center => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                center.id;


            option.textContent =
                `${center.name} — ${center.distance_km} km`;


            select.appendChild(
                option
            );
        }
    );
}


/* =========================================================
   AGENT SLOT DROPDOWN
   ========================================================= */

function populateAgentSlotDropdown(
    center
) {

    const slotSelect =
        document.getElementById(
            "agentSlotSelect"
        );


    if (!slotSelect) {
        return;
    }


    slotSelect.innerHTML = `

        <option value="">
            Select service slot
        </option>

    `;


    slotSelect.disabled =
        true;


    if (
        !center ||
        !center.available_slots ||
        center.available_slots.length === 0
    ) {

        return;
    }


    center.available_slots.forEach(
        slot => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                slot;


            option.textContent =
                slot;


            slotSelect.appendChild(
                option
            );
        }
    );


    slotSelect.disabled =
        false;
}


/* =========================================================
   CENTER CHANGE
   ========================================================= */

const centerSelect =
    document.getElementById(
        "agentServiceCenterSelect"
    );


if (centerSelect) {

    centerSelect.addEventListener(
        "change",
        function () {

            const centerId =
                Number(
                    this.value
                );


            selectedAgentCenter =
                agentServiceCenters.find(
                    center =>
                        center.id ===
                        centerId
                );


            if (!selectedAgentCenter) {

                const distance =
                    document.getElementById(
                        "agentServiceDistance"
                    );


                if (distance) {
                    distance.textContent = "";
                }


                populateAgentSlotDropdown(
                    null
                );


                selectedAgentSlot =
                    null;


                return;
            }


            const distance =
                document.getElementById(
                    "agentServiceDistance"
                );


            if (distance) {

                distance.textContent =
                    `${selectedAgentCenter.distance_km} km away`;
            }


            populateAgentSlotDropdown(
                selectedAgentCenter
            );


            if (
                selectedAgentCenter.available_slots &&
                selectedAgentCenter.available_slots.length
            ) {

                const slotSelect =
                    document.getElementById(
                        "agentSlotSelect"
                    );


                selectedAgentSlot =
                    selectedAgentCenter
                        .available_slots[0];


                if (slotSelect) {

                    slotSelect.value =
                        selectedAgentSlot;
                }
            }
        }
    );
}


/* =========================================================
   SLOT CHANGE
   ========================================================= */

const slotSelect =
    document.getElementById(
        "agentSlotSelect"
    );


if (slotSelect) {

    slotSelect.addEventListener(
        "change",
        function () {

            selectedAgentSlot =
                this.value ||
                null;
        }
    );
}


/* =========================================================
   RUN AIDM AGENT
   ========================================================= */

async function runAIDMAgent() {

    if (!appliance) {
        return;
    }


    const button =
        document.getElementById(
            "runAgentButton"
        );


    const status =
        document.getElementById(
            "agentStatus"
        );


    if (button) {

        button.disabled =
            true;

        button.innerHTML =
            "⏳ AIDM Agent is working...";
    }


    if (status) {

        status.innerHTML = `

            <div class="alert alert-info">

                <strong>
                    Agent is analyzing your appliance...
                </strong>

                <p class="mb-0 mt-1">

                    Finding maintenance date,
                    service centers and available slots.

                </p>

            </div>

        `;
    }


    try {

        const response =
            await fetch(

                `${API_URL}/agent/run` +

                `?user_id=${encodeURIComponent(
                    userId
                )}` +

                `&appliance_id=${encodeURIComponent(
                    appliance.id
                )}` +

                `&location=Pune` +

                `&confirm_booking=false`,

                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Agent request failed."
            );
        }


        const agentResults =
            document.getElementById(
                "agentResults"
            );


        if (agentResults) {

            agentResults.style.display =
                "block";
        }


        const agentMaintenanceStatus =
            document.getElementById(
                "agentMaintenanceStatus"
            );


        if (agentMaintenanceStatus) {

            agentMaintenanceStatus.textContent =
                data.maintenance_status ||
                "-";
        }


        const agentMaintenanceDate =
            document.getElementById(
                "agentMaintenanceDate"
            );


        if (agentMaintenanceDate) {

            agentMaintenanceDate.textContent =
                data.next_maintenance_date ||
                "-";
        }


        agentServiceCenters =
            data.service_centers ||
            [];


        const agentCenterCount =
            document.getElementById(
                "agentCenterCount"
            );


        if (agentCenterCount) {

            agentCenterCount.textContent =
                agentServiceCenters.length;
        }


        populateAgentCenterDropdown();


        let recommendedCenter =
            data.recommended_service_center;


        if (!recommendedCenter) {

            recommendedCenter =
                agentServiceCenters[0];
        }


        if (recommendedCenter) {

            selectedAgentCenter =
                agentServiceCenters.find(
                    center =>
                        center.id ===
                        recommendedCenter.id
                ) ||
                recommendedCenter;


            if (centerSelect) {

                centerSelect.value =
                    selectedAgentCenter.id;
            }


            const distance =
                document.getElementById(
                    "agentServiceDistance"
                );


            if (distance) {

                distance.textContent =
                    `${selectedAgentCenter.distance_km} km away`;
            }


            populateAgentSlotDropdown(
                selectedAgentCenter
            );


            selectedAgentSlot =
                data.recommended_slot ||
                selectedAgentCenter
                    .available_slots?.[0] ||
                null;


            if (slotSelect) {

                slotSelect.value =
                    selectedAgentSlot ||
                    "";
            }
        }


        const agentExplanation =
            document.getElementById(
                "agentExplanation"
            );


        if (agentExplanation) {

            agentExplanation.textContent =
                data.maintenance_explanation ||
                "No explanation available.";
        }


        const confirmation =
            document.getElementById(
                "agentConfirmation"
            );


        if (confirmation) {

            confirmation.style.display =
                (
                    selectedAgentCenter &&
                    selectedAgentSlot
                )
                    ? "block"
                    : "none";
        }


        window.aidmRecommendation = {

            serviceCenterId:
                selectedAgentCenter
                    ? selectedAgentCenter.id
                    : null,

            bookingDate:
                data.next_maintenance_date,

            recommendedSlot:
                selectedAgentSlot
        };


        if (status) {

            status.innerHTML = `

                <div class="alert alert-success">

                    <strong>
                        ✅ Agent analysis completed.
                    </strong>

                    <p class="mb-0 mt-1">

                        You can now choose a service center
                        and available time slot.

                    </p>

                </div>

            `;
        }


    } catch (error) {

        console.error(
            "AIDM Agent Error:",
            error
        );


        if (status) {

            status.innerHTML = `

                <div class="alert alert-danger">

                    <strong>
                        Agent Error
                    </strong>

                    <p class="mb-0 mt-1">

                        ${escapeHtml(
                            error.message
                        )}

                    </p>

                </div>

            `;
        }


    } finally {

        if (button) {

            button.disabled =
                false;

            button.innerHTML =
                "🤖 Run AIDM Agent";
        }
    }
}


/* =========================================================
   RUN AGENT BUTTON
   ========================================================= */

const runAgentButton =
    document.getElementById(
        "runAgentButton"
    );


if (runAgentButton) {

    runAgentButton.addEventListener(
        "click",
        runAIDMAgent
    );
}


/* =========================================================
   CONFIRM AGENT BOOKING
   ========================================================= */

const confirmAgentBooking =
    document.getElementById(
        "confirmAgentBooking"
    );


if (confirmAgentBooking) {

    confirmAgentBooking.addEventListener(
        "click",
        async function () {

            const centerSelect =
                document.getElementById(
                    "agentServiceCenterSelect"
                );


            const slotSelect =
                document.getElementById(
                    "agentSlotSelect"
                );


            const selectedCenterId =
                Number(
                    centerSelect.value
                );


            const selectedSlot =
                slotSelect.value;


            if (
                !selectedCenterId ||
                !selectedSlot
            ) {

                alert(
                    "Please select a service center and time slot."
                );

                return;
            }


            if (!appliance) {

                alert(
                    "Please select an appliance first."
                );

                return;
            }


            const recommendation =
                window.aidmRecommendation;


            if (
                !recommendation ||
                !recommendation.bookingDate
            ) {

                alert(
                    "Maintenance date is missing."
                );

                return;
            }


            const button =
                document.getElementById(
                    "confirmAgentBooking"
                );


            const resultBox =
                document.getElementById(
                    "agentBookingResult"
                );


            button.disabled =
                true;


            button.innerHTML =
                "⏳ Booking...";


            try {

                const response =
                    await fetch(

                        `${API_URL}/agent/run` +

                        `?user_id=${encodeURIComponent(
                            userId
                        )}` +

                        `&appliance_id=${encodeURIComponent(
                            appliance.id
                        )}` +

                        `&location=Pune` +

                        `&selected_service_center=${encodeURIComponent(
                            selectedCenterId
                        )}` +

                        `&booking_date=${encodeURIComponent(
                            recommendation.bookingDate
                        )}` +

                        `&booking_slot=${encodeURIComponent(
                            selectedSlot
                        )}` +

                        `&confirm_booking=true`,

                        {
                            method: "POST"
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Booking failed."
                    );
                }


                if (
                    data.booking_status !==
                    "CONFIRMED"
                ) {

                    throw new Error(
                        "Booking was not confirmed."
                    );
                }


                resultBox.style.display =
                    "block";


                resultBox.innerHTML = `

                    <div class="alert alert-success">

                        <strong>
                            ✅ Appointment booked successfully!
                        </strong>


                        <p class="mb-1 mt-2">

                            Booking ID:

                            <strong>

                                ${escapeHtml(
                                    data.booking_id
                                )}

                            </strong>

                        </p>


                        <p class="mb-1">

                            Date:

                            <strong>

                                ${escapeHtml(
                                    data.booking_date
                                )}

                            </strong>

                        </p>


                        <p class="mb-1">

                            Appliance:

                            <strong>

                                ${escapeHtml(
                                    appliance.model
                                )}

                            </strong>

                        </p>


                        <p class="mb-0">

                            Time Slot:

                            <strong>

                                ${escapeHtml(
                                    data.booking_slot ||
                                    selectedSlot
                                )}

                            </strong>

                        </p>

                    </div>

                `;


                const confirmation =
                    document.getElementById(
                        "agentConfirmation"
                    );


                if (confirmation) {

                    confirmation.style.display =
                        "none";
                }


                button.innerHTML =
                    "✅ Booking Confirmed";


                await loadBookingHistory();


            } catch (error) {

                console.error(
                    "Agent Booking Error:",
                    error
                );


                resultBox.style.display =
                    "block";


                resultBox.innerHTML = `

                    <div class="alert alert-danger">

                        <strong>
                            Booking failed
                        </strong>

                        <p class="mb-0 mt-1">

                            ${escapeHtml(
                                error.message
                            )}

                        </p>

                    </div>

                `;


                button.disabled =
                    false;


                button.innerHTML =
                    "✅ Yes, Book It";
            }
        }
    );
}


/* =========================================================
   CANCEL AGENT BOOKING
   ========================================================= */

const cancelAgentBooking =
    document.getElementById(
        "cancelAgentBooking"
    );


if (cancelAgentBooking) {

    cancelAgentBooking.addEventListener(
        "click",
        function () {

            const confirmation =
                document.getElementById(
                    "agentConfirmation"
                );


            if (confirmation) {

                confirmation.style.display =
                    "none";
            }


            const status =
                document.getElementById(
                    "agentStatus"
                );


            if (status) {

                status.innerHTML = `

                    <div class="alert alert-secondary">

                        <strong>
                            Booking not created.
                        </strong>

                        <p class="mb-0 mt-1">

                            The recommendation has been
                            dismissed.

                        </p>

                    </div>

                `;
            }
        }
    );
}


/* =========================================================
   ADD APPLIANCE BUTTON
   ========================================================= */

const addApplianceButton =
    document.getElementById(
        "addApplianceButton"
    );


if (addApplianceButton) {

    addApplianceButton.addEventListener(
        "click",
        function () {

            const section =
                document.getElementById(
                    "registerApplianceSection"
                );


            if (!section) {
                return;
            }


            section.style.display =
                "block";


            section.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    );
}


/* =========================================================
   REGISTER APPLIANCE
   ========================================================= */

const applianceForm =
    document.getElementById(
        "applianceForm"
    );


if (applianceForm) {

    applianceForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const message =
                document.getElementById(
                    "applianceMessage"
                );


            const applianceType =
                document.getElementById(
                    "applianceTypeInput"
                ).value;


            const brand =
                document.getElementById(
                    "brandInput"
                ).value;


            const model =
                document.getElementById(
                    "modelInput"
                ).value;


            const interval =
                document.getElementById(
                    "intervalInput"
                ).value;


            const installationDate =
                document.getElementById(
                    "installationDate"
                ).value;


            const lastServiceDate =
                document.getElementById(
                    "lastServiceDate"
                ).value;


            /* Only the three current KENT manuals */

            const allowedModels = [

                "KENT Elegant",

                "KENT Grand",

                "KENT Sterling Star"

            ];


            if (
                applianceType !==
                    "Water Purifier" ||

                brand !== "KENT" ||

                !allowedModels.includes(
                    model
                )
            ) {

                message.innerHTML = `

                    <div class="alert alert-warning">

                        Please select:

                        <strong>
                            Water Purifier
                        </strong>

                        →

                        <strong>
                            KENT
                        </strong>

                        →

                        <strong>
                            KENT Elegant,
                            KENT Grand,
                            or
                            KENT Sterling Star
                        </strong>

                    </div>

                `;

                return;
            }


            try {

                const response =
                    await fetch(
                        `${API_URL}/appliances/`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    user_id:
                                        Number(
                                            userId
                                        ),

                                    appliance_type:
                                        applianceType,

                                    brand:
                                        brand,

                                    model:
                                        model,

                                    installation_date:
                                        installationDate,

                                    last_service_date:
                                        lastServiceDate,

                                    maintenance_interval:
                                        Number(
                                            interval
                                        )
                                })
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Unable to register appliance"
                    );
                }


                message.innerHTML = `

                    <div class="alert alert-success">

                        Appliance registered successfully!

                        Loading your new appliance...

                    </div>

                `;


                applianceForm.reset();


                document.getElementById(
                    "registerApplianceSection"
                ).style.display =
                    "none";


                document.getElementById(
                    "dashboardContent"
                ).style.display =
                    "block";


                const appliancesSection =
                    document.getElementById(
                        "appliancesSection"
                    );


                if (appliancesSection) {

                    appliancesSection.style.display =
                        "block";
                }


                /* Add new appliance */

                appliances.push(
                    data
                );


                /* Select new appliance */

                await selectAppliance(
                    data.id,
                    true
                );


                message.innerHTML =
                    "";


            } catch (error) {

                console.error(
                    "Registration Error:",
                    error
                );


                message.innerHTML = `

                    <div class="alert alert-danger">

                        ${escapeHtml(
                            error.message
                        )}

                    </div>

                `;
            }
        }
    );
}


/* =========================================================
   START DASHBOARD
   ========================================================= */

loadAppliances()
    .then(function () {

        updateAskAIDMModel();

        return loadBookingHistory();

    })
    .catch(function (error) {

        console.error(
            "Dashboard startup error:",
            error
        );

    });