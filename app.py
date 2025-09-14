import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Trend Edge Scanner")

st.write("BOOT 1: app.py loaded")

# ---- Load & prepare config from Secrets (read-only) ----
try:
    sec = st.secrets
    st.write("BOOT 2: secrets loaded")
    st.json({
        "credentials": "ok" if "credentials" in sec else "missing",
        "cookie": "ok" if "cookie" in sec else "missing",
    })

    # Build a *mutable* credentials dict from the read-only secrets
    raw_users = sec["credentials"]["usernames"]
    creds_usernames = {}
    for uname, u in raw_users.items():
        creds_usernames[uname] = {
            "email": u["email"],
            "name": u["name"],
            "password": u["password"],  # <-- bcrypt hash from your Secrets
        }
    credentials = {"usernames": creds_usernames}

    cookie_cfg = sec["cookie"]
    cookie_name = cookie_cfg["name"]
    cookie_key = cookie_cfg["key"]
    cookie_expiry = int(cookie_cfg.get("expiry_days", 30))

    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR loading secrets / preparing configs")
    st.exception(e)
    st.stop()

# ---- Create authenticator ----
try:
    authenticator = stauth.Authenticate(
        credentials,   # <-- plain Python dict (mutable)
        cookie_name,
        cookie_key,
        cookie_expiry,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---- Login form ----
try:
    # v0.4.2 returns None until the form is submitted
    auth_result = authenticator.login("Login", location="main")

    if auth_result is None:
        # Form not submitted yet; stop the script cleanly
        st.stop()

    # After form submit, this is a tuple
    name, auth_status, username = auth_result

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---- Main routing ----
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("✓ Logged in — put your main app content here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your username and password.")
