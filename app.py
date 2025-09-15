# app.py
import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")
st.write("BOOT 1: app.py loaded")

# ---------- Load & prep secrets ----------
try:
    sec = st.secrets  # TOML from Streamlit Cloud
    users_src = sec["credentials"]["usernames"]   # table [credentials.usernames]
    # make a plain dict copy for streamlit-authenticator
    credentials = {"usernames": {u: dict(users_src[u]) for u in users_src}}

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

# ---------- Authenticator ----------
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
    login_result = authenticator.login("Login", "main")

    # If the form hasn't been submitted yet
    if login_result is None:
        st.stop()

    # Once submitted, unpack into name, auth_status, username
    name, auth_status, username = login_result
    st.write(f"DEBUG login_result unpacked: {login_result}")

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

    # After submit: expected tuple -> (name, auth_status, username)
    try:
        name, auth_status, username = login_result
    except Exception:
        st.error("Unexpected login() return format")
        st.write(login_result)
        st.stop()
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---------- Main routing ----------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # --- Demo content so we can see something ---
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
