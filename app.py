import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", page_icon="📈", layout="wide")

st.write("BOOT 1: app.py loaded")

# ---------- Load secrets ----------
try:
    credentials = st.secrets["credentials"]      # from Secrets Manager
    cookie_cfg  = st.secrets["cookie"]
    st.write("BOOT 2: secrets loaded")
except Exception as e:
    st.error("ERROR loading secrets")
    st.exception(e)
    st.stop()

# ---------- Prepare cookie values ----------
try:
    cookie_name = cookie_cfg["name"]
    cookie_key  = cookie_cfg["key"]
    # expiry may be int or string; cast to int
    cookie_days = int(cookie_cfg["expiry_days"])
    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR preparing credentials & cookie")
    st.exception(e)
    st.stop()

# ---------- Authenticator ----------
try:
    import streamlit_authenticator as stauth

    authenticator = stauth.Authenticate(
        credentials,     # the whole [credentials] table
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
try:
    # returns (name, auth_status, username) AFTER the user submits;
    # returns None while waiting for input
    auth_result = authenticator.login("Login", location="main")

    if auth_result is None:
        st.stop()  # show the form and wait

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
    st.write("You're logged in. Main content goes here.")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your username and password.")

