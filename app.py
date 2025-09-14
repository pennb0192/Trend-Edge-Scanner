import streamlit as st
import streamlit_authenticator as stauth

# --- BOOT 1 ---
st.write("BOOT 1: app.py loaded")

# --- Load secrets ---
try:
    credentials = st.secrets["credentials"]
    cookie = st.secrets["cookie"]
    cookie_name = cookie["name"]
    cookie_key = cookie["key"]
    cookie_expiry = cookie["expiry_days"]
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# --- Authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials,           # full [credentials] table from TOML
        cookie_name,           # cookie name
        cookie_key,            # cookie key
        cookie_expiry          # cookie expiry
    )
    st.write("BOOT 3: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# --- Login UI ---
try:
    name, auth_status, username = authenticator.login("Login", "main")
    st.write("BOOT 4: login form rendered")
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# --- Routing ---
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("BOOT 5: Logged in, main content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please enter your username and password")
