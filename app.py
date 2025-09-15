import json
import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Trend Edge Scanner", layout="centered")

st.write("BOOT 1: app.py loaded")

# ---- Load & prepare secrets -------------------------------------------------
try:
    # sanity log
    st.write("BOOT 2: secrets loaded")
    st.json({
        "credentials": "ok" if "credentials" in st.secrets else "missing",
        "cookie": "ok" if "cookie" in st.secrets else "missing",
    })

    # Convert Streamlit Secrets object into plain Python dicts
    # (streamlit_authenticator mutates the dict internally; Secrets is read-only)
    credentials = json.loads(json.dumps(st.secrets["credentials"]))
    cookie = json.loads(json.dumps(st.secrets["cookie"]))

    cookie_name = cookie.get("name")
    cookie_key = cookie.get("key")
    cookie_expiry = int(cookie.get("expiry_days", 30))

    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# ---- Create authenticator ---------------------------------------------------
try:
    authenticator = stauth.Authenticate(
        credentials,       # full [credentials] table as a plain dict
        cookie_name,       # cookie name
        cookie_key,        # signature key
        cookie_expiry,     # expiry days (int)
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---- Login form --------------------------------------------------------------
try:
    # streamlit-authenticator v0.4.2: `login(location="main")`
    # It returns None until the user submits; then returns (name, auth_status, username)
    auth_result = authenticator.login(location="main")

    if auth_result is None:
        # Form not submitted yet; stop the script cleanly so only the form shows
        st.stop()

    name, auth_status, username = auth_result

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---- Main routing ------------------------------------------------------------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("✅ Logged in — put your main app content here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your username and password.")
