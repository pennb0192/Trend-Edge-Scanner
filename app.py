import streamlit as st
import streamlit_authenticator as stauth

# Load user credentials from secrets.toml
d = st.secrets["credentials"]["usernames"]["pennb0192"]
u = {"email": d["email"], "name": d["name"], "password": d["password"]}

credentials = {
    "usernames": {
        "pennb0192": u
    }
}

# Cookie settings
cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

# Setup authenticator (No preauthorized anymore)
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"]
)

# Login form
name, auth_status, username = authenticator.login("Login", "main")

# Login logic
if auth_status == False:
    st.error("Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your credentials")
elif auth_status:
    st.success(f"Welcome {name} 👋🏽")
    # 🔍 Scanner goes here (import scanner.py if needed)
    st.write("🔎 Trend Scanner is ready!")
