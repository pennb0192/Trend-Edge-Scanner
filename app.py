# ---- Main routing ----
if auth_status:
    # show a logout button in the sidebar
    authenticator.logout("Logout", "sidebar")

    # visible confirmation you’re in
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # --- DEMO CONTENT so you can see something ---
    st.write("This is placeholder content that only shows when you are authenticated.")
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

    # remove this debug line later if you like
    st.write({"BOOT 7": "logged in, main content rendered", "auth_status": auth_status})

elif auth_status is False:
    st.error("Username/password is incorrect.")
else:
    st.info("Please log in.")
