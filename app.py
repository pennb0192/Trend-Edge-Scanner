import streamlit as st
import streamlit_authenticator as stauth

# 1. --- Credentials and Cookie Setup ---
credentials = {
    "usernames": {
        "pennb0192": {
            "email": st.secrets["credentials"]["usernames"]["pennb0192"]["email"],
            "name": st.secrets["credentials"]["usernames"]["pennb0192"]["name"],
            "password": st.secrets["credentials"]["usernames"]["pennb0192"]["password"]
        }
    }
}

cookie = {
    "name": st.secrets["cookie"]["name"],
    "key": st.secrets["cookie"]["key"],
    "expiry_days": st.secrets["cookie"]["expiry_days"]
}

# 2. --- Authenticator Setup ---
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"]
)

# 3. --- Login Form (place this before your app logic) ---
name, auth_status, username = authenticator.login(
    form_name="Login",
    location="main"
)

# 4. --- Login Logic ---
if auth_status == False:
    st.error("Invalid username or password 😕")
elif auth_status is None:
    st.warning("Please enter your credentials")
elif auth_status:
    st.success(f"Welcome {name} 👋")
    st.write("📈 Trend Scanner is ready!")

    # Your app logic goes here, below the login gate
    # Example:
    st.write("This is where your scanner UI and results will appear.")
