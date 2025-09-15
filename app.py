# app.py
import json
import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")

st.write("BOOT 1: app.py loaded")

# ---------- Load & prepare secrets ----------
try:
    # We expect your Streamlit secrets to be in TOML like:
    # [credentials.usernames.pennb0192]
    # email = "pennb.0192@gmail.com"
    # name  = "pennb0192"
    # password = "$2b$12$...."  (bcrypt hash)
    #
    # [cookie]
    # name = "trend_edge_auth"
    # key  = "549852344888"
    # expiry_days = 30
    sec = st.secrets  # immutable mapping

    # Make *mutable* copies for streamlit-authenticator
    src_users = sec["credentials"]["usernames"]
    usernames = {u: dict(src_users[u]) for u in src_users}  # plain dict copy
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

# ---------- Import and create authenticator ----------
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
    # v0.4.x returns None until the form is submitted
    auth_result = authenticator.login("main")
    if auth_result is None:
        st.stop()

    # After submit: tuple -> (name, auth_status, username)
    name, auth_status, username = auth_result
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---------- Main routing ----------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # --- Demo content so you can see something after login ---
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
    st.info("Please log in.")
