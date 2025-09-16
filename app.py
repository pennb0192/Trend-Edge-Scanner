import streamlit as st
import streamlit_authenticator as stauth

# 🔐 Load credentials from secrets.toml
d = st.secrets["credentials"]["usernames"]["pennb0192"]
u = {"email": d["email"], "name": d["name"], "password": d["password"]}

credentials = {
    "usernames": {
        "pennb0192": u
    }
}

cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

# ✅ Create the authenticator (NOTE: preauthorized is no longer passed here)
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"]
)

# 🔐 User login
name, auth_status, username = authenticator.login("Login", "main")

# 🚨 Handle login responses
if auth_status is False:
    st.error("Invalid username or password")

elif auth_status is None:
    st.warning("Please enter your credentials")

elif auth_status:
    # 🧠 Add user registration section (optional)
    with st.expander("🔐 Register a New User"):
        try:
            if authenticator.register_user(preauthorization=False):
                st.success("User registered successfully!")
        except Exception as e:
            st.error(e)

    # ✅ Logged in section
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name} 👋")

    st.title("📊 TrendEdge Scanner Dashboard")
    st.write("You're now logged in and can access all features.")
    
    # 🔧 Placeholder: Add your scanner logic here
    st.info("🚧 Scanner UI coming soon...")

