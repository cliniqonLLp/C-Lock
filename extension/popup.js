const API_BASE = "https://c-lock-1.onrender.com";

const loginBox = document.getElementById("loginBox");
const sessionBox = document.getElementById("sessionBox");
const userEmail = document.getElementById("userEmail");
const errorBox = document.getElementById("error");

document.getElementById("loginBtn").addEventListener("click", login);
document.getElementById("logoutBtn").addEventListener("click", logout);

async function getStoredSession() {
    return await chrome.storage.local.get([
        "access_token",
        "refresh_token",
        "user_email",
        "user_name"
    ]);
}

async function setStoredSession(data) {
    await chrome.storage.local.set({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        user_email: data.email,
        user_name: data.name
    });
}

async function clearStoredSession() {
    await chrome.storage.local.remove([
        "access_token",
        "refresh_token",
        "user_email",
        "user_name"
    ]);
}

async function refreshToken(refreshToken) {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            refresh_token: refreshToken
        })
    });

    const data = await res.json();

    if (!data.success) {
        await clearStoredSession();
        return false;
    }

    await chrome.storage.local.set({
        access_token: data.access_token,
        refresh_token: data.refresh_token
    });

    return true;
}

async function verifySession() {
    const session = await getStoredSession();

    if (!session.access_token || !session.refresh_token) {
        showLogin();
        return;
    }

    let res = await fetch(`${API_BASE}/auth/me`, {
        headers: {
            "Authorization": "Bearer " + session.access_token
        }
    });

    if (res.status === 401) {
        const ok = await refreshToken(session.refresh_token);

        if (!ok) {
            showLogin();
            return;
        }

        const updated = await getStoredSession();

        res = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                "Authorization": "Bearer " + updated.access_token
            }
        });
    }

    if (!res.ok) {
        await clearStoredSession();
        showLogin();
        return;
    }

    const me = await res.json();
    showSession(me.email);
}

async function login() {
    errorBox.textContent = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!data.success) {
        errorBox.textContent = data.message || "Login failed";
        return;
    }

    await setStoredSession(data);
    showSession(data.email);
}

// async function logout() {
//     const session = await getStoredSession();

//     await fetch(`${API_BASE}/auth/logout`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//             refresh_token: session.refresh_token
//         })
//     });

//     await chrome.storage.local.clear(); 
// }
async function logout() {
    const session = await getStoredSession();

    if (session.refresh_token) {
        await fetch(`${API_BASE}/auth/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                refresh_token: session.refresh_token
            })
        });
    }

    await chrome.storage.local.clear();

    loginBox.style.display = "block";
    sessionBox.style.display = "none";
    userEmail.textContent = "";
    errorBox.textContent = "";
}

function showLogin() {
    loginBox.style.display = "block";
    sessionBox.style.display = "none";
}

function showSession(email) {
    loginBox.style.display = "none";
    sessionBox.style.display = "block";
    userEmail.textContent = email;
}

verifySession();