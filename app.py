# app.py
import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")
st.write("BOOT 1: app.py loaded")

# ---------- Load & prepare secrets ----------
try:
    sec = st.secrets  # immutable mapping
    # Make mutable copies for streamlit-authenticator
    src_users = sec["credentials"]["usernames"]
    credentials = {"usernames": {u: dict(src_users[u]) for u in src_users}}

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

# ---------- Import and create authenticator ----------
try:
    import streamlit_authenticator as stauth

    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        cookie_days,
    )
    st.write("BOOT 4: streamlit_authenticator imported")
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---------- Login UI (robust) ----------
try:
    # Use keywords so the version can't confuse args
    try:
        auth_result = authenticator.login(form_name="Login", location="main")
    except TypeError:
        # very old versions only accept location
        auth_result = authenticator.login("main")
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# Figure out auth status no matter which version you have
name = username = None
auth_status = None

if auth_result is not None:
    # 0.4.x returns a tuple AFTER submit
    name, auth_status, username = auth_result
else:
    # Sometimes 0.4.x returns None on rerun; pull from session_state
    auth_status = st.session_state.get("authentication_status")
    name = st.session_state.get("name")
    username = st.session_state.get("username")

st.write("DEBUG auth_status:", auth_status)  # you can remove later

# ---------- Main routing ----------
if auth_status is True:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # Demo content (so you see something)
    st.write("This content only shows when you are authenticated.")
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
    # Not logged in yet (or awaiting form submit)
    st.info("Please log in above.")
