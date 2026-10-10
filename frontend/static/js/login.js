// Login page: show/hide the password and prevent double submission.
(function () {
    "use strict";

    const form = document.getElementById("login-form");
    if (!form) return;

    const password = document.getElementById("password");
    const toggle = document.getElementById("toggle-password");
    const submit = document.getElementById("login-submit");

    toggle.addEventListener("click", () => {
        const show = password.type === "password";
        password.type = show ? "text" : "password";
        toggle.textContent = show ? "Hide" : "Show";
        toggle.setAttribute("aria-pressed", String(show));
    });

    // The browser's required-field validation runs before "submit" fires,
    // so the form is valid by the time we get here.
    form.addEventListener("submit", () => {
        submit.disabled = true;
        submit.textContent = "Signing in…";
    });

    // Re-enable the button if the user comes back with the browser's Back button.
    window.addEventListener("pageshow", () => {
        submit.disabled = false;
        submit.textContent = "Sign in";
    });
})();
