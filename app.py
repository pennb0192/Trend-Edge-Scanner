import streamlit as st
import streamlit_authenticator as stauth

# --- Load secrets ---
st.write("BOOT 1: app.py loaded")
try:
    credentials = st.secrets["credentials"]
    cookie = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

st.write("BOOT 3: credentials & cookie prepared")

# --- Create authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials,                # pass full [credentials] from TOML
        cookie["name"],             # cookie name
        cookie["key"],              # cookie key
        cookie["expiry_days"],      # cookie expiry
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# --- Login UI ---
try:
    name, auth_status, username = authenticator.login("Login", "main")

    if auth_status:
        authenticator.logout("Logout", "sidebar")
        st.success(f"Welcome, {name}!")
        st.title("Trend Edge Scanner")
        st.write("BOOT 7: logged in, main content goes here.")

    elif auth_status is False:
        st.error("Username/password is incorrect")

    elif auth_status is None:
        st.warning("Please enter your username and password")
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()
