
const API_URL = "http://127.0.0.1:8000";


/* =========================
   SHOW REGISTER
========================= */

document
    .getElementById("showRegister")
    .addEventListener("click", function () {
        document.getElementById("loginSection").style.display = "none";
        document.getElementById("registerSection").style.display = "block";
    });


/* =========================
   SHOW LOGIN
========================= */

document
    .getElementById("showLogin")
    .addEventListener("click", function () {
        document.getElementById("registerSection").style.display = "none";
        document.getElementById("loginSection").style.display = "block";
    });


/* =========================
   REGISTER
========================= */

document
    .getElementById("registerForm")
    .addEventListener("submit", async function (event) {
        event.preventDefault();

        const name = document
            .getElementById("registerName")
            .value.trim();

        const email = document
            .getElementById("registerEmail")
            .value.trim();

        const password = document
            .getElementById("registerPassword")
            .value;

        const location = document
            .getElementById("registerLocation")
            .value.trim();

        const message = document.getElementById("registerMessage");

        if (!name || !email || !password || !location) {
            message.textContent = "";

            const alert = document.createElement("div");
            alert.className = "alert alert-danger";
            alert.textContent = "Please fill in all fields.";

            message.appendChild(alert);
            return;
        }

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name,
                    email,
                    password,
                    location
                })
            });

            const data = await response.json();

            if (!response.ok) {
                message.textContent = "";

                const alert = document.createElement("div");
                alert.className = "alert alert-danger";
                alert.textContent =
                    typeof data.detail === "string"
                        ? data.detail
                        : "Registration failed. Please check your details.";

                message.appendChild(alert);
                return;
            }

            message.textContent = "";

            const alert = document.createElement("div");
            alert.className = "alert alert-success";
            alert.textContent =
                "Account created successfully! You can now log in.";

            message.appendChild(alert);

            document.getElementById("registerForm").reset();

        } catch (error) {
            message.textContent = "";

            const alert = document.createElement("div");
            alert.className = "alert alert-danger";
            alert.textContent = "Unable to connect to AIDM server.";

            message.appendChild(alert);
            console.error(error);
        }
    });


/* =========================
   LOGIN
========================= */

document
    .getElementById("loginForm")
    .addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document
            .getElementById("loginEmail")
            .value.trim();

        const password = document
            .getElementById("loginPassword")
            .value;

        const message = document.getElementById("loginMessage");

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email,
                    password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                message.textContent = "";

                const alert = document.createElement("div");
                alert.className = "alert alert-danger";
                alert.textContent =
                    typeof data.detail === "string"
                        ? data.detail
                        : "Login failed. Please check your details.";

                message.appendChild(alert);
                return;
            }

            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("user_name", data.name);
            localStorage.setItem("user_email", data.email);

            if (data.location) {
                localStorage.setItem("user_location", data.location);
            } else {
                localStorage.removeItem("user_location");
            }

            window.location.href = "dashboard.html";

        } catch (error) {
            message.textContent = "";

            const alert = document.createElement("div");
            alert.className = "alert alert-danger";
            alert.textContent = "Unable to connect to AIDM server.";

            message.appendChild(alert);
            console.error(error);
        }
    });
