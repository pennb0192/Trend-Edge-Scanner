import streamlit as st
import streamlit_authenticator as stauth
from collections.abc import Mapping

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")
st.write("BOOT 1: app.py loaded")

# ---------- helpers ----------
def deep_copy(obj):
    """Convert Streamlit Secrets (read-only mappings) into plain Python dicts/lists."""
    if isinstance(obj, Mapping):
        return {k: deep_copy(obj[k]) for k in obj.keys()}
    if isinstance(obj, (list, tuple)):
        return [deep_copy(v) for v in obj]
    return obj

# ---------- load secrets ----------
try:
    credentials_src = st.secrets["credentials"]
    cookie_src = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# make them mutable plain dicts
credentials = deep_copy(credentials_src)
cookie = deep_copy(cookie_src)
st.write("BOOT 3: credentials & cookie prepared")

# ---------- create authenticator ----------
try:
    authenticator = stauth.Authenticate(
        credentials,                      # full [credentials] table from TOML
        cookie["name"],                   # cookie name
        cookie["key"],                    # cookie key
        cookie.get("expiry_days", 30),    # expiry
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---------- login UI ----------
try:
    # v0.4.2 uses login(location, form_name) – use keywords to avoid order issues
    auth_result = authenticator.login(location="main", form_name="Login")

    if auth_result is None:
        st.stop()  # user hasn’t submitted yet

    name, auth_status, username = auth_result
    st.write(f"BOOT 6: login called; auth_status={auth_status}")
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---------- main routing ----------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("BOOT 7: logged in, main content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your credentials.")
