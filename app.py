import streamlit as st
import streamlit_authenticator as stauth

# --- Load credentials and cookie settings from secrets.toml ---
credentials = st.secrets["credentials"]

cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

# --- Authenticator Setup ---
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"]
)

# --- Login Form ---
name, auth_status, username = authenticator.login("Login", "main")

# --- Login Logic ---
if auth_status == False:
    st.error("Invalid username or password ❌")
elif auth_status is None:
    st.warning("Please enter your credentials 👈🏾")
elif auth_status:
    st.success(f"Welcome {name} 👋🏾")
    st.write("✅ Trend Scanner is ready!")
