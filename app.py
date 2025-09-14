import streamlit as st
import streamlit_authenticator as stauth

st.write("BOOT 1: app.py loaded")

# Load secrets
credentials = st.secrets["credentials"]
cookie = st.secrets["cookie"]

st.write("BOOT 2: secrets loaded")

# Create the authenticator
try:
    authenticator = stauth.Authenticate(
        credentials,
        cookie["name"],
        cookie["key"],
        cookie["expiry_days"],
    )
    st.write("BOOT 3: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# Login form
try:
    name, auth_status, username = authenticator.login("Login", "main")
    st.write("BOOT 4: login attempted")
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# Main content routing
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("BOOT 5: logged in, main content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
elif auth_status is None:
    st.warning("Please enter your username and password")
