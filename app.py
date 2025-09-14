import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")

st.write("BOOT 1: app.py loaded")

# ---- Load secrets from TOML ----
try:
    credentials = st.secrets["credentials"]          # whole [credentials] table
    cookie_cfg   = st.secrets["cookie"]              # whole [cookie] table
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# ---- Prepare cookie settings ----
try:
    cookie_name = cookie_cfg.get("name", "trend_edge_auth")
    cookie_key  = cookie_cfg.get("key", "change_me")
    cookie_days = int(cookie_cfg.get("expiry_days", 30))
    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing cookie settings")
    st.exception(e)
    st.stop()

# ---- Create authenticator ----
try:
    authenticator = stauth.Authenticate(
        credentials,   # expects the [credentials] table from TOML
        cookie_name,
        cookie_key,
        cookie_days,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---- Login UI ----
try:
    # Use either positional OR keyword for location (not both).
    auth_result = authenticator.login("Login", "main")  # <- positional is simplest

    if auth_result is None:
        st.stop()  # wait for user to submit the form

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
    st.write("You are logged in. Main content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please log in to continue.")
