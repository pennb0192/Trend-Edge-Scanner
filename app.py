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

cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

# Authenticator setup (no preauthorized anymore)
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"]
)

# Login form (correct keyword here: main without quotes)
name, auth_status, username = authenticator.login("Login", location="main")

# Login logic
if auth_status == False:
    st.error("Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your credentials")
elif auth_status:
    st.success(f"Welcome {name} 👋🏽")
    # 🔍 Scanner goes here (import scanner.py if needed)
    st.write("🔍 Trend Scanner is ready!")
