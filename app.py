import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Trend Edge Scanner")

st.write("BOOT 1: app.py loaded")

# ---------- Load secrets ----------
try:
    raw_credentials = st.secrets["credentials"]   # read-only object
    raw_cookie = st.secrets["cookie"]             # read-only object
    st.write("BOOT 2: secrets loaded")
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# ---------- Convert to mutable dicts ----------
# Build a plain-Python dict from st.secrets so the library can mutate it
credentials = {"usernames": {}}
for user, data in raw_credentials["usernames"].items():
    credentials["usernames"][user] = {
        "email": data["email"],
        "name": data["name"],
        "password": data["password"],
    }

cookie_name = raw_cookie.get("name", "trend_edge_auth")
cookie_key = raw_cookie.get("key", "change_this_key")
cookie_days = int(raw_cookie.get("expiry_days", 30))

st.write("BOOT 3: credentials & cookie prepared")

# ---------- Create authenticator ----------
try:
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        cookie_days,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---------- Login UI ----------
try:
    # NOTE: label first, then location (as keyword)
    auth_result = authenticator.login("Login", location="main")

    # When the form hasn’t been submitted yet, login() returns None
    if auth_result is None:
        st.stop()

    name, auth_status, username = auth_result
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---------- Main routing ----------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("Logged in — put your main content here.")
else:
    st.error("Username or password is incorrect")
