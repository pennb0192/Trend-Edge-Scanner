import streamlit as st
import streamlit_authenticator as stauth

# ---------------- BOOT 1 ----------------
st.write("BOOT 1: app.py loaded")

# ---------------- BOOT 2 ----------------
try:
    credentials = st.secrets["credentials"]
    cookie = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
    st.write({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# ---------------- BOOT 3 ----------------
try:
    cookie_name = cookie["name"]
    cookie_key = cookie["key"]
    cookie_days = cookie["expiry_days"]
    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing credentials/cookie")
    st.exception(e)
    st.stop()

# ---------------- BOOT 4 ----------------
try:
    st.write("BOOT 4: streamlit_authenticator imported")
except Exception as e:
    st.error("ERROR importing streamlit_authenticator")
    st.exception(e)
    st.stop()

# ---------------- BOOT 5 ----------------
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

# ---------------- LOGIN ----------------
try:
    # Correct call: (form_name, location)
    auth_result = authenticator.login("Login", "main")

    if auth_result is None:
        st.stop()

    name, auth_status, username = auth_result
    st.write(f"BOOT 6: login called; auth_status={auth_status}")
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---------------- MAIN ROUTING ----------------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("BOOT 7: logged in, main content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please enter your username and password")
