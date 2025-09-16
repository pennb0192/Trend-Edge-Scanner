import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load secrets from .streamlit/secrets.toml
credentials = {
    "usernames": {
        "pennb0192": {
            "email": st.secrets["credentials"]["usernames.pennb0192.email"],
            "name": st.secrets["credentials"]["usernames.pennb0192.name"],
            "password": st.secrets["credentials"]["usernames.pennb0192.password"]
        }
    }
}

# Cookie settings
cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

# Authenticator setup
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"]
)

# Login form
name, auth_status, username = authenticator.login("Login", location="main")

if auth_status == False:
    st.error("Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your credentials")
elif auth_status:
    st.success(f"Welcome {name} 👋🏾")
    st.write("🔍 Trend Scanner is ready!")
