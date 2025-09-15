import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Trend Edge Scanner")

st.write("BOOT 1: app.py loaded")

# ---- Load and normalize secrets ----
try:
    # Pull from Streamlit Secrets
    raw_credentials = st.secrets["credentials"]
    raw_cookie      = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# Convert Secrets (read-only mapping) -> regular dicts
def to_plain_dict(secrets_mapping):
    # handles nested Secrets objects as plain dicts
    return {k: (to_plain_dict(v) if hasattr(v, "keys") else v) for k, v in secrets_mapping.items()}

credentials = to_plain_dict(raw_credentials)
cookie      = to_plain_dict(raw_cookie)

st.write("BOOT 3: credentials & cookie prepared")

# ---- Create authenticator ----
try:
    cookie_name   = cookie.get("name", "app_auth")
    cookie_key    = cookie.get("key", "change_me")
    cookie_expiry = cookie.get("expiry_days", 30)

    authenticator = stauth.Authenticate(
        credentials,     # MUST be a plain dict, not Secrets
        cookie_name,
        cookie_key,
        cookie_expiry,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---- Login form ----
try:
    # streamlit-authenticator v0.4.2 returns None until the form is submitted
    auth_result = authenticator.login("Login", "main")  # form_name, location

    if auth_result is None:
        # Form not submitted yet — pause the script so the page renders the form
        st.stop()

    # After submit, this is a (name, auth_status, username) tuple
    name, auth_status, username = auth_result

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ---- Main routing ----
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("You are logged in — put your main app content here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your username and password.")
