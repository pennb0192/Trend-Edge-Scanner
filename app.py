import streamlit as st
import streamlit_authenticator as stauth

# --- BOOT 1: app.py loaded ---
st.write("BOOT 1: app.py loaded")

# --- BOOT 2: load secrets ---
try:
    credentials = st.secrets["credentials"]
    cookie_cfg = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# --- BOOT 3: prepare credentials & cookie ---
try:
    cookie_name = cookie_cfg.get("name")
    cookie_key = cookie_cfg.get("key")
    cookie_days = cookie_cfg.get("expiry_days")

    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing credentials")
    st.exception(e)
    st.stop()

# --- BOOT 4: import authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        cookie_days,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# --- BOOT 6: Login UI ---
try:
    # CORRECTED CALL: no duplicate location argument
    auth_result = authenticator.login(location="main", form_name="Login")

    if auth_result is None:
        st.write("Waiting for credentials...")
        st.stop()

    name, auth_status, username = auth_result
    st.write(f"BOOT 6: login called; auth_status={auth_status}")

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# --- BOOT 7: Main routing ---
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("BOOT 7: logged in, main content goes here.")

elif auth_status is False:
    st.error("Username/password is incorrect")

else:
    st.warning("Please enter your username and password")
