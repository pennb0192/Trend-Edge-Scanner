import streamlit as st
import traceback

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")

st.write("BOOT 1: app.py loaded")

# ---- Try to read secrets safely ----
try:
    sec = st.secrets
    st.write("BOOT 2: secrets loaded")
    st.write({
        "credentials": "ok" if "credentials" in sec else "missing",
        "cookie": "ok" if "cookie" in sec else "missing",
    })
except Exception as e:
    st.error("ERROR reading secrets")
    st.exception(e)
    st.stop()

# ---- Build credentials & cookie config ----
try:
    creds_src = sec["credentials"]["usernames"]
    usernames = {
        u: {
            "email": d["email"],
            "name": d["name"],
            "password": d["password"],
        }
        for u, d in creds_src.items()
    }
    credentials = {"usernames": usernames}

    cookie_cfg = sec["cookie"]
    cookie_name = cookie_cfg.get("name", "trend_edge_auth")
    cookie_key = cookie_cfg.get("key", "replace_me_key")
    cookie_days = int(cookie_cfg.get("expiry_days", 30))

    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR building credentials from secrets")
    st.exception(e)
    st.stop()

# ---- Import authenticator ----
try:
    import streamlit_authenticator as stauth
    st.write("BOOT 4: streamlit_authenticator imported")
except Exception as e:
    st.error("ERROR importing streamlit_authenticator")
    st.exception(e)
    st.stop()

# ---- Create authenticator ----
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

# ---- Login UI ----
try:
    # v0.4.2: (location, form_name) and returns None until you submit
    auth_result = authenticator.login("main", "Login")

    if auth_result is None:
        # Form not submitted yet — show the form and stop cleanly
        st.stop()

    # After submit, unpack (name, auth_status, username)
    name, auth_status, username = auth_result
    st.write("BOOT 6: login called", {"auth_status": auth_status})

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---- Main routing ----
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("Logged in — main app content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect.")
else:
    st.info("Please enter your **username** (not email) and password, then click **Login**.")
