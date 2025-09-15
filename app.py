# app.py
import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")
st.write("BOOT 1: app.py loaded")

# ---------- Load & prepare secrets ----------
try:
    sec = st.secrets  # TOML in Streamlit Secrets
    src_users = sec["credentials"]["usernames"]
    usernames = {u: dict(src_users[u]) for u in src_users}          # make it mutable
    credentials = {"usernames": usernames}

    cookie_cfg = sec["cookie"]
    cookie_name = cookie_cfg.get("name", "trend_edge_auth")
    cookie_key = cookie_cfg.get("key", "replace_me")
    cookie_days = int(cookie_cfg.get("expiry_days", 30))

    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR loading/preparing secrets")
    st.exception(e)
    st.stop()

# ---------- Import & create authenticator ----------
try:
    import streamlit_authenticator as stauth
    st.write("BOOT 4: streamlit_authenticator imported")

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
    # v0.4.x: call login() and read results from session_state
    authenticator.login(location="main")

    auth_status = st.session_state.get("authentication_status", None)
    name = st.session_state.get("name", None)
    username = st.session_state.get("username", None)

    # debug line (safe to leave in while testing)
    st.write("DEBUG auth_status:", auth_status)
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---------- Main routing ----------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # Demo content so you can see something
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Demo Metric", "42", "+3")
    with col2:
        st.write("Upload a CSV to test:")
        f = st.file_uploader("Choose a CSV", type=["csv"])
        if f is not None:
            import pandas as pd
            df = pd.read_csv(f)
            st.dataframe(df.head())

elif auth_status is False:
    st.error("Username/password is incorrect.")
else:
    st.info("Please log in.")
