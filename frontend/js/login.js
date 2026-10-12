const API_URL = "http://127.0.0.1:8000";


/* =========================
   SHOW REGISTER
========================= */

document
    .getElementById("showRegister")
    .addEventListener("click", function() {

        document.getElementById("loginSection").style.display = "none";

        document.getElementById("registerSection").style.display = "block";

    });


/* =========================
   SHOW LOGIN
========================= */

document
    .getElementById("showLogin")
    .addEventListener("click", function() {

        document.getElementById("registerSection").style.display = "none";

        document.getElementById("loginSection").style.display = "block";

    });


/* =========================
   REGISTER
========================= */

document
    .getElementById("registerForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const name =
            document.getElementById("registerName").value;

        const email =
            document.getElementById("registerEmail").value;

        const password =
            document.getElementById("registerPassword").value;

        const message =
            document.getElementById("registerMessage");


        try {

            const response = await fetch(
                `${API_URL}/auth/register`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {

                message.innerHTML = `
                    <div class="alert alert-danger">
                        ${data.detail}
                    </div>
                `;

                return;
            }


            message.innerHTML = `
                <div class="alert alert-success">
                    Account created successfully! You can now login.
                </div>
            `;


            document.getElementById("registerForm").reset();


        } catch (error) {

            message.innerHTML = `
                <div class="alert alert-danger">
                    Unable to connect to AIDM server.
                </div>
            `;

            console.error(error);

        }

    });


/* =========================
   LOGIN
========================= */

document
    .getElementById("loginForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();


        const email =
            document.getElementById("loginEmail").value;

        const password =
            document.getElementById("loginPassword").value;

        const message =
            document.getElementById("loginMessage");


        try {

            const response = await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {

                message.innerHTML = `
                    <div class="alert alert-danger">
                        ${data.detail}
                    </div>
                `;

                return;
            }


            localStorage.setItem(
                "user_id",
                data.user_id
            );

            localStorage.setItem(
                "user_name",
                data.name
            );

            localStorage.setItem(
                "user_email",
                data.email
            );


            window.location.href =
                "dashboard.html";

        } catch (error) {

            message.innerHTML = `
                <div class="alert alert-danger">
                    Unable to connect to AIDM server.
                </div>
            `;

            console.error(error);

        }

    });