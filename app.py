import streamlit as st
import streamlit_authenticator as stauth

st.write("BOOT 1: app.py loaded")

# --- Load & validate secrets ---
try:
    raw_creds = st.secrets["credentials"]   # TOML mapping (read-only)
    raw_cookie = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# --- Convert Secrets to a normal dict the library can use ---
try:
    # Build the credentials dict expected by streamlit_authenticator
    credentials = {"usernames": {}}
    for uname, info in raw_creds.get("usernames", {}).items():
        credentials["usernames"][uname] = {
            "name": info.get("name"),
            "email": info.get("email"),
            "password": info.get("password"),
        }

    cookie_name = raw_cookie.get("name")
    cookie_key = raw_cookie.get("key")
    cookie_expiry = int(raw_cookie.get("expiry_days", 30))

    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing credentials/cookie")
    st.exception(e)
    st.stop()

# --- Create authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name=cookie_name,
        key=cookie_key,
        cookie_expiry_days=cookie_expiry,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ---- Login form ----
try:
    # Show login form
    name, auth_status, username = authenticator.login(
        form_name="Login",
        location="main"
    )

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()


    name, auth_status, username = auth_result
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# --- Main routing ---
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}!")
    st.title("Trend Edge Scanner")
    st.write("✅ Logged in — put your main app content here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your username and password.")
