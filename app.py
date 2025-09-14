import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Trend Edge Scanner", layout="centered")

# --- Boot Step 1 ---
st.write("BOOT 1: app.py loaded")

# --- Load secrets ---
try:
    credentials = st.secrets["credentials"]
    cookie = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# --- Prepare credentials & cookie ---
try:
    cookie_name = cookie["name"]
    cookie_key = cookie["key"]
    cookie_expiry = cookie["expiry_days"]

    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing credentials & cookie")
    st.exception(e)
    st.stop()

# --- Create authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        cookie_expiry,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# --- Login UI ---
try:
    # Location must be "main" or "sidebar"
    auth_result = authenticator.login("main")

    if auth_result is None:
        st.warning("Please enter your credentials")
        st.stop()

    name, auth_status, username = auth_result
    st.write(f"BOOT 6: login called; auth_status={auth_status}")

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# --- Main routing ---
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("BOOT 7: logged in, main content goes here.")

elif auth_status is False:
    st.error("Username/password is incorrect")

elif auth_status is None:
    st.warning("Please enter your username and password")
