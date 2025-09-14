import streamlit as st
import streamlit_authenticator as stauth

# ---- Boot step 1 ----
st.write("BOOT 1: app.py loaded")

# ---- Load secrets ----
try:
    credentials = st.secrets["credentials"]
    cookie = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# ---- Prepare credentials & cookie ----
try:
    cookie_name = cookie["name"]
    cookie_key = cookie["key"]
    cookie_expiry = cookie["expiry_days"]
    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing credentials & cookie")
    st.exception(e)
    st.stop()

# ---- Create authenticator ----
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

# ---- Login form ----
try:
    # v0.4.2 returns None until form is submitted
    auth_result = authenticator.login("main", "Login")

    if auth_result is None:
        st.stop()

    # After submit, returns (name, auth_status, username)
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
    st.write("✔ Logged in – put your main app content here.")

elif auth_status is False:
    st.error("Username/password is incorrect")

else:
    st.info("Please enter your username and password.")
