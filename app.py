import streamlit as st
import streamlit_authenticator as stauth

st.write("BOOT 1: app.py loaded")

# --- Load secrets from Streamlit Cloud ---
try:
    credentials = st.secrets["credentials"]   # expects [credentials] table
    cookie = st.secrets["cookie"]             # expects [cookie] table
    st.write("BOOT 2: secrets loaded")
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

st.write("BOOT 3: credentials & cookie prepared")

# --- Create authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials,
        cookie["name"],
        cookie["key"],
        cookie["expiry_days"]
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# --- Login form ---
try:
    name, auth_status, username = authenticator.login("Login", location="main")

    if auth_status is False:
        st.error("Username/password is incorrect")
    elif auth_status is None:
        st.warning("Please enter your username and password")
    else:
        st.success(f"Welcome {name}")
        st.write("You are now logged in!")
        authenticator.logout("Logout", "sidebar")

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()
