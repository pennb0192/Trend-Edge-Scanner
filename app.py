import streamlit as st
import streamlit_authenticator as stauth

# Load nested credentials
d = st.secrets["credentials"]["usernames"]["pennb0192"]
u = {"email": d["email"], "name": d["name"], "password": d["password"]}

credentials = {
    "usernames": {
        "pennb0192": u
    }
}

cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

preauthorized = {
    "emails": st.secrets["preauthorized"]["emails"]
}

authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"],
    preauthorized
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status == False:
    st.error("Invalid username or password")

if auth_status == None:
    st.warning("Please enter your credentials")

if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name}")
    st.title("✅ Login Success!")
