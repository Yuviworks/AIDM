const API_URL =
    "http://127.0.0.1:8000";


/* =========================
   GET STORED DATA
========================= */

const userId =
    localStorage.getItem("user_id");


const serviceCenterId =
    localStorage.getItem(
        "selected_service_center"
    );


const applianceId =
    localStorage.getItem(
        "selected_appliance"
    );


/* =========================
   CHECK REQUIRED DATA
========================= */

if (
    !userId ||
    !serviceCenterId ||
    !applianceId
) {

    alert(
        "Booking information is missing."
    );

    window.location.href =
        "dashboard.html";

}


/* =========================
   VARIABLES
========================= */

let selectedAppliance = null;

let selectedServiceCenter = null;

let selectedBookingSlot = null;


/* =========================
   LOAD APPLIANCE
========================= */

async function loadAppliance() {

    try {

        const response =
            await fetch(
                `${API_URL}/appliances/user/${userId}`
            );


        const appliances =
            await response.json();


        if (!response.ok) {

            throw new Error(
                appliances.detail ||
                "Unable to load appliance"
            );

        }


        const appliance =
            appliances.find(
                item =>
                    item.id ===
                    Number(applianceId)
            );


        if (!appliance) {

            throw new Error(
                "Selected appliance not found."
            );

        }


        selectedAppliance =
            appliance;


        /* =========================
           DISPLAY APPLIANCE
        ========================= */

        const applianceElement =
            document.getElementById(
                "applianceInfo"
            );


        if (applianceElement) {

            applianceElement.innerHTML = `

                <div class="card border-0 bg-light">

                    <div class="card-body">

                        <h5 class="fw-bold mb-3">

                            ${appliance.appliance_type}

                        </h5>

                        <p class="mb-1">

                            <strong>
                                Brand:
                            </strong>

                            ${appliance.brand}

                        </p>

                        <p class="mb-0">

                            <strong>
                                Model:
                            </strong>

                            ${appliance.model}

                        </p>

                    </div>

                </div>

            `;

        }


        /* =========================
           LOAD SERVICE CENTER
        ========================= */

        await loadServiceCenter(
            appliance.brand
        );


    } catch (error) {

        console.error(
            "Appliance loading error:",
            error
        );


        const applianceElement =
            document.getElementById(
                "applianceInfo"
            );


        if (applianceElement) {

            applianceElement.innerHTML = `

                <div class="alert alert-danger">

                    ${error.message}

                </div>

            `;

        }

    }

}


/* =========================
   LOAD SERVICE CENTER
========================= */

async function loadServiceCenter(
    brand
) {

    try {

        const response =
            await fetch(

                `${API_URL}/service/centers` +
                `?brand=${encodeURIComponent(
                    brand
                )}` +
                `&location=Pune`

            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load service center"
            );

        }


        const center =
            data.service_centers.find(
                item =>
                    item.id ===
                    Number(serviceCenterId)
            );


        if (!center) {

            throw new Error(
                "Selected service center not found."
            );

        }


        selectedServiceCenter =
            center;


        /* =========================
           DISPLAY SERVICE CENTER
        ========================= */

        const nameElement =
            document.getElementById(
                "serviceCenterName"
            );


        const locationElement =
            document.getElementById(
                "serviceCenterLocation"
            );


        const phoneElement =
            document.getElementById(
                "serviceCenterPhone"
            );


        const availabilityElement =
            document.getElementById(
                "serviceCenterAvailability"
            );


        if (nameElement) {

            nameElement.textContent =
                center.name;

        }


        if (locationElement) {

            locationElement.textContent =
                `📍 ${center.location}`;

        }


        if (phoneElement) {

            phoneElement.textContent =
                `📞 ${center.phone}`;

        }


        if (availabilityElement) {

            availabilityElement.textContent =
                `🕒 ${center.availability}`;

        }


    } catch (error) {

        console.error(
            "Service center loading error:",
            error
        );


        const message =
            document.getElementById(
                "bookingMessage"
            );


        if (message) {

            message.innerHTML = `

                <div class="alert alert-danger">

                    ${error.message}

                </div>

            `;

        }

    }

}


/* =========================
   FIND AVAILABLE SLOT
========================= */

function findSlotForDate(
    bookingDate
) {

    if (
        !selectedServiceCenter ||
        !selectedServiceCenter.available_slots
    ) {

        return null;

    }


    const matchingSlot =
        selectedServiceCenter.available_slots.find(
            slot =>
                slot.startsWith(
                    bookingDate
                )
        );


    return matchingSlot || null;

}


/* =========================
   BOOKING FORM
========================= */

const bookingForm =
    document.getElementById(
        "bookingForm"
    );


if (bookingForm) {

    bookingForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const bookingDate =
                document.getElementById(
                    "bookingDate"
                ).value;


            const confirmationCheckbox =
                document.getElementById(
                    "confirmationCheckbox"
                );


            const button =
                document.getElementById(
                    "bookButton"
                );


            const message =
                document.getElementById(
                    "bookingMessage"
                );


            /* =========================
               DATE CHECK
            ========================= */

            if (!bookingDate) {

                message.innerHTML = `

                    <div class="alert alert-warning">

                        Please select a service date.

                    </div>

                `;

                return;

            }


            /* =========================
               CONFIRMATION CHECK
            ========================= */

            if (
                confirmationCheckbox &&
                !confirmationCheckbox.checked
            ) {

                message.innerHTML = `

                    <div class="alert alert-warning">

                        Please confirm that you want
                        to book this maintenance service.

                    </div>

                `;

                return;

            }


            /* =========================
               FIND AVAILABLE SLOT
            ========================= */

            selectedBookingSlot =
                findSlotForDate(
                    bookingDate
                );


            if (!selectedBookingSlot) {

                message.innerHTML = `

                    <div class="alert alert-warning">

                        <strong>
                            No available slot found.
                        </strong>

                        <p class="mb-0 mt-1">

                            Please select a date that has
                            an available service slot.

                        </p>

                    </div>

                `;

                return;

            }


            /* =========================
               LOADING
            ========================= */

            button.disabled = true;


            button.textContent =
                "🤖 Agent is booking...";


            message.innerHTML = `

                <div class="alert alert-info">

                    <strong>
                        🤖 AIDM Booking Agent is working...
                    </strong>

                    <p class="mb-0 mt-1">

                        The agent is confirming the service
                        request and creating your appointment.

                    </p>

                </div>

            `;


            try {

                /* =========================
                   CALL AGENT
                ========================= */

                const url =

                    `${API_URL}/agent/run` +

                    `?user_id=${encodeURIComponent(
                        userId
                    )}` +

                    `&appliance_id=${encodeURIComponent(
                        applianceId
                    )}` +

                    `&location=Pune` +

                    `&selected_service_center=${encodeURIComponent(
                        serviceCenterId
                    )}` +

                    `&booking_date=${encodeURIComponent(
                        bookingDate
                    )}` +

                    `&booking_slot=${encodeURIComponent(
                        selectedBookingSlot
                    )}` +

                    `&confirm_booking=true`;


                const response =
                    await fetch(
                        url,
                        {
                            method: "POST"
                        }
                    );


                const data =
                    await response.json();


                /* =========================
                   ERROR
                ========================= */

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Booking failed."
                    );

                }


                /* =========================
                   CONFIRMED
                ========================= */

                if (
                    data.booking_status ===
                    "CONFIRMED"
                ) {

                    message.innerHTML = `

                        <div class="alert alert-success">

                            <h5 class="fw-bold">

                                ✅ Booking Confirmed

                            </h5>


                            <p class="mb-1">

                                Your maintenance appointment
                                was successfully created by
                                the AIDM Booking Agent.

                            </p>


                            <p class="mb-1">

                                <strong>
                                    Booking ID:
                                </strong>

                                #${data.booking_id}

                            </p>


                            <p class="mb-1">

                                <strong>
                                    Service Date:
                                </strong>

                                ${data.booking_date}

                            </p>


                            <p class="mb-0">

                                <strong>
                                    Service Slot:
                                </strong>

                                ${
                                    data.booking_slot ||
                                    selectedBookingSlot
                                }

                            </p>

                        </div>


                        <button
                            type="button"
                            id="dashboardButton"
                            class="btn btn-primary w-100 mt-3"
                        >
                            Return to Dashboard
                        </button>

                    `;


                    const dashboardButton =
                        document.getElementById(
                            "dashboardButton"
                        );


                    if (dashboardButton) {

                        dashboardButton.addEventListener(
                            "click",
                            function () {

                                window.location.href =
                                    "dashboard.html";

                            }
                        );

                    }


                    button.style.display =
                        "none";


                } else {

                    throw new Error(
                        "Booking was not confirmed."
                    );

                }


            } catch (error) {

                console.error(
                    "Agent Booking Error:",
                    error
                );


                message.innerHTML = `

                    <div class="alert alert-danger">

                        <strong>
                            ❌ Booking Failed
                        </strong>

                        <p class="mb-0 mt-1">

                            ${error.message}

                        </p>

                    </div>

                `;

            } finally {

                if (
                    button.style.display !==
                    "none"
                ) {

                    button.disabled = false;


                    button.textContent =
                        "🤖 Confirm & Book with AIDM Agent";

                }

            }

        }
    );

}


/* =========================
   INITIALIZE PAGE
========================= */

loadAppliance();