import streamlit as st
import streamlit_authenticator as stauth

# --- build a mutable credentials dict from st.secrets ---
sec = st.secrets["auth_config"]

# copy usernames out of the read-only secrets object
usernames = {}
for user, data in sec["credentials"]["usernames"].items():
    usernames[user] = {
        "email": data["email"],
        "name": data["name"],
        "password": data["password"],
    }

credentials = {"usernames": usernames}

# cookie config (normal dict)
cookie_cfg = {
    "name": sec["cookie"]["name"],
    "key": sec["cookie"]["key"],
    "expiry_days": int(sec["cookie"]["expiry_days"]),
}

# authenticator now receives mutable dicts (no more mutation error)
authenticator = stauth.Authenticate(
    credentials,
    cookie_cfg["name"],
    cookie_cfg["key"],
    cookie_cfg["expiry_days"],
)
