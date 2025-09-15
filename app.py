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

# ---------- Login UI ----------
# NOTE: In st-authenticator 0.4.x the API returns a tuple (name, status, username).
# Before the form is submitted it returns (None, None, None).
try:
    name, auth_status, username = authenticator.login("main")  # location ONLY
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# Helpful, temporary debug line. You can delete later.
st.write(f"DEBUG → auth_status={auth_status} user={username}")

# ---------- Main routing ----------
if auth_status is True:
    # show a logout button in the sidebar
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
    # auth_status is None (form not submitted yet or cookie not validated)
    st.info("Please log in above to continue.")
    st.stop()
