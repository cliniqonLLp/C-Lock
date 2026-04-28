const API_BASE = "https://c-lock-1.onrender.com";

let isFilling = false;
let alreadyFilled = false;

function setReactLikeValue(element, value) {
    const prototype =
        element instanceof HTMLTextAreaElement
            ? window.HTMLTextAreaElement.prototype
            : window.HTMLInputElement.prototype;

    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    const setter = descriptor && descriptor.set;

    element.focus();

    if (setter) {
        setter.call(element, value);
    } else {
        element.value = value;
    }

    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
    element.dispatchEvent(new Event("blur", { bubbles: true }));
}

function isUsableInput(el) {
    return !!el && !el.disabled && !el.readOnly;
}

function pickBest(candidates) {
    for (const el of candidates) {
        if (isUsableInput(el)) return el;
    }
    return null;
}

function findUsernameField() {
    const candidates = [
        ...document.querySelectorAll("input[name='id']"),
        ...document.querySelectorAll("input[name='email']"),
        ...document.querySelectorAll("input[type='email']"),
        ...document.querySelectorAll("input[autocomplete='username']"),
        ...document.querySelectorAll("input[name*='email' i]"),
        ...document.querySelectorAll("input[name*='user' i]"),
        ...document.querySelectorAll("input[name*='login' i]"),
        ...document.querySelectorAll("input[id*='email' i]"),
        ...document.querySelectorAll("input[id*='user' i]"),
        ...document.querySelectorAll("input[placeholder*='email' i]"),
        ...document.querySelectorAll("input[placeholder*='user' i]"),
        ...document.querySelectorAll("input[type='text']")
    ];

    return pickBest(candidates);
}

function findPasswordField() {
    const candidates = [
        ...document.querySelectorAll("input[name='password']"),
        ...document.querySelectorAll("input[type='password']"),
        ...document.querySelectorAll("input[autocomplete='current-password']"),
        ...document.querySelectorAll("input[name*='pass' i]"),
        ...document.querySelectorAll("input[id*='pass' i]"),
        ...document.querySelectorAll("input[placeholder*='pass' i]")
    ];

    return pickBest(candidates);
}

function looksLikeLoginPage() {
    const usernameField = findUsernameField();
    const passwordField = findPasswordField();

    if (!usernameField || !passwordField) return false;

    const url = window.location.href.toLowerCase();
    const pageText = document.body ? document.body.innerText.toLowerCase() : "";

    const hints = [
        "login",
        "log in",
        "sign in",
        "signin",
        "password",
        "email",
        "username"
    ];

    const hasHintInUrl = hints.some(
        h => url.includes(h.replace(" ", "")) || url.includes(h)
    );

    const hasHintInText = hints.some(
        h => pageText.includes(h)
    );

    return hasHintInUrl || hasHintInText;
}

async function getStoredTokens() {
    return await chrome.storage.local.get([
        "access_token",
        "refresh_token",
        "user_email",
        "user_name"
    ]);
}

async function saveTokens(accessToken, refreshToken) {
    await chrome.storage.local.set({
        access_token: accessToken,
        refresh_token: refreshToken
    });
}

async function clearTokens() {
    await chrome.storage.local.remove([
        "access_token",
        "refresh_token",
        "user_email",
        "user_name"
    ]);
}

async function refreshAccessToken(refreshToken) {
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
        await clearTokens();
        throw new Error("C-Lock session expired. Please login again from extension popup.");
    }

    await saveTokens(data.access_token, data.refresh_token);

    return data.access_token;
}

async function apiFetch(url, options = {}) {
    const tokens = await getStoredTokens();

    if (!tokens.access_token || !tokens.refresh_token) {
        throw new Error("Not logged in to C-Lock. Open the extension popup and login.");
    }

    options.headers = options.headers || {};
    options.headers["Authorization"] = "Bearer " + tokens.access_token;

    let res = await fetch(url, options);

    if (res.status === 401) {
        const newAccessToken = await refreshAccessToken(tokens.refresh_token);
        options.headers["Authorization"] = "Bearer " + newAccessToken;
        res = await fetch(url, options);
    }

    return res;
}

async function getVaultMatches(domain) {
    const res = await apiFetch(`${API_BASE}/vault/match`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ domain })
    });

    if (!res.ok) {
        throw new Error("Vault match failed: " + res.status);
    }

    return await res.json();
}

async function requestFillToken(selectedCredential, domain) {
    const res = await apiFetch(`${API_BASE}/fill/request`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            credential_type: selectedCredential.credential_type,
            credential_id: selectedCredential.credential_id,
            domain: domain
        })
    });

    if (!res.ok) {
        throw new Error("Fill request failed: " + res.status);
    }

    return await res.json();
}

async function redeemFillToken(fillToken) {
    const res = await fetch(`${API_BASE}/fill/redeem`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            fill_token: fillToken
        })
    });

    if (!res.ok) {
        throw new Error("Fill redeem failed: " + res.status);
    }

    return await res.json();
}

function getRememberKey(domain) {
    return "clock_last_" + domain;
}

function rememberCredential(domain, match) {
    localStorage.setItem(
        getRememberKey(domain),
        JSON.stringify({
            credential_type: match.credential_type,
            credential_id: match.credential_id
        })
    );
}

function getRememberedCredential(domain, matches) {
    const saved = localStorage.getItem(getRememberKey(domain));

    if (!saved) return null;

    try {
        const parsed = JSON.parse(saved);

        return matches.find(
            m =>
                m.credential_type === parsed.credential_type &&
                m.credential_id === parsed.credential_id
        ) || null;
    } catch (err) {
        console.warn("C-Lock: failed to parse remembered credential", err);
        return null;
    }
}

function chooseCredential(matches) {
    return new Promise((resolve) => {
        if (!matches || matches.length === 0) {
            resolve(null);
            return;
        }

        const domain = window.location.hostname;

        if (matches.length === 1) {
            rememberCredential(domain, matches[0]);
            resolve(matches[0]);
            return;
        }

        // const remembered = getRememberedCredential(domain, matches);

        // if (remembered) {
        //     console.log("C-Lock: using remembered account");
        //     resolve(remembered);
        //     return;
        // }

        const existing = document.getElementById("clock-picker");
        if (existing) existing.remove();

        const box = document.createElement("div");
        box.id = "clock-picker";
        box.style.position = "fixed";
        box.style.top = "20px";
        box.style.right = "20px";
        box.style.zIndex = "999999";
        box.style.background = "white";
        box.style.border = "1px solid #ddd";
        box.style.borderRadius = "12px";
        box.style.boxShadow = "0 8px 30px rgba(0,0,0,0.15)";
        box.style.padding = "14px";
        box.style.width = "310px";
        box.style.fontFamily = "Arial, sans-serif";
        box.style.color = "#111";

        const title = document.createElement("div");
        title.textContent = "C-Lock";
        title.style.fontWeight = "700";
        title.style.fontSize = "16px";
        title.style.marginBottom = "8px";

        const subtitle = document.createElement("div");
        subtitle.textContent = "Choose an account to fill";
        subtitle.style.fontSize = "13px";
        subtitle.style.color = "#555";
        subtitle.style.marginBottom = "12px";

        box.appendChild(title);
        box.appendChild(subtitle);

        matches.forEach((match) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.style.display = "block";
            btn.style.width = "100%";
            btn.style.textAlign = "left";
            btn.style.marginBottom = "8px";
            btn.style.padding = "10px";
            btn.style.border = "1px solid #ddd";
            btn.style.borderRadius = "8px";
            btn.style.background = "#f8f8f8";
            btn.style.cursor = "pointer";
            btn.style.color = "#111";

            btn.innerHTML = `
                <div style="font-weight:600;">${escapeHtml(match.label)}</div>
                <div style="font-size:12px;color:#555;">${escapeHtml(match.username)}</div>
                <div style="font-size:11px;color:#888;">${escapeHtml(match.credential_type)}</div>
            `;

            btn.addEventListener("mouseenter", () => {
                btn.style.background = "#eeeeee";
            });

            btn.addEventListener("mouseleave", () => {
                btn.style.background = "#f8f8f8";
            });

            btn.addEventListener("click", () => {
                rememberCredential(domain, match);
                box.remove();
                resolve(match);
            });

            box.appendChild(btn);
        });

        const cancel = document.createElement("button");
        cancel.type = "button";
        cancel.textContent = "Cancel";
        cancel.style.display = "block";
        cancel.style.width = "100%";
        cancel.style.marginTop = "6px";
        cancel.style.padding = "8px";
        cancel.style.border = "none";
        cancel.style.background = "transparent";
        cancel.style.cursor = "pointer";
        cancel.style.color = "#777";

        cancel.addEventListener("click", () => {
            box.remove();
            resolve(null);
        });

        const changeHint = document.createElement("div");
        changeHint.textContent = "Tip: clear remembered account from site storage if you want the picker again.";
        changeHint.style.fontSize = "11px";
        changeHint.style.color = "#999";
        changeHint.style.marginTop = "8px";
        changeHint.style.lineHeight = "1.3";

        box.appendChild(cancel);
        box.appendChild(changeHint);

        document.body.appendChild(box);
    });
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function tryFill() {
    if (isFilling || alreadyFilled) return;
    if (!looksLikeLoginPage()) return;

    const usernameField = findUsernameField();
    const passwordField = findPasswordField();

    if (!usernameField || !passwordField) return;
    if (usernameField.value || passwordField.value) return;

    isFilling = true;

    try {
        const domain = window.location.hostname;
        console.log("C-Lock domain:", domain);

        const matchData = await getVaultMatches(domain);
        console.log("C-Lock match response:", matchData);

        if (!matchData.matches || matchData.matches.length === 0) {
            console.log("C-Lock: no matches");
            return;
        }

        const selectedCredential = await chooseCredential(matchData.matches);

        if (!selectedCredential) {
            console.log("C-Lock: user cancelled selection");
            return;
        }

        const fillData = await requestFillToken(selectedCredential, domain);
        console.log("C-Lock fill request response:", fillData);

        if (!fillData.success || !fillData.fill_token) {
            console.log("C-Lock: fill request failed");
            return;
        }

        const credentialData = await redeemFillToken(fillData.fill_token);
        console.log("C-Lock redeem success:", credentialData.success);

        if (!credentialData.success) {
            console.log("C-Lock: redeem failed");
            return;
        }

        setReactLikeValue(usernameField, credentialData.username);
        setReactLikeValue(passwordField, credentialData.password);
        credentialData.username = null;
        credentialData.password = null;

        alreadyFilled = true;
        console.log("C-Lock: fill complete");
    } catch (err) {l
        console.error("C-Lock error:", err);
    } finally {
        isFilling = false;
    }
}

setTimeout(tryFill, 1000);
setTimeout(tryFill, 2500);