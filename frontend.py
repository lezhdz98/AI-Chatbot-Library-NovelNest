import streamlit as st
import requests

st.title("Library Support Chatbot")

# Store session state
if "selected_user" not in st.session_state:
    st.session_state.selected_user = "(New User)"
if "existing_sessions" not in st.session_state:
    st.session_state.existing_sessions = []
st.session_state.new_user = ""

# Fetch existing sessions
def fetch_sessions():
    response = requests.get("http://127.0.0.1:5000/sessions")
    if response.status_code == 200:
        st.session_state.existing_sessions = response.json().get("sessions", [])

fetch_sessions()  # Load sessions at start

# Select an existing session or create a new one
selected_user = st.selectbox(
    "Select an existing session:", 
    ["(New User)"] + st.session_state.existing_sessions, 
    index=(["(New User)"] + st.session_state.existing_sessions).index(st.session_state.selected_user)
)

# Disable new user input if an existing user is selected
new_user = st.text_input("Or create a new session:", disabled=(selected_user != "(New User)"), value=st.session_state.new_user)

# Button to create/select session
if st.button("Start Chat"):
    if selected_user != "(New User)":
        st.session_state.selected_user = selected_user
    elif new_user:
        # Check if new_user already exists in the existing sessions
        if new_user in st.session_state.existing_sessions:
            st.warning(f"The session name '{new_user}' already exists. Please choose a different name.")
        else:
            response = requests.post("http://127.0.0.1:5000/new_session", json={'session_name': new_user})
            if response.status_code == 200:
                st.session_state.selected_user = new_user  # Auto-select new session
                fetch_sessions()  # Refresh the dropdown
                st.success(response.json()["message"])
                st.rerun()  # Force a rerun to reflect the new session in the UI
            else:
                st.error("Failed to create session.")
    else:
        st.warning("Please select an existing session or enter a new name.")

# Chat input (only when a session is selected and user is not creating a new session)
if st.session_state.selected_user != "(New User)" and selected_user != "(New User)":
    user_input = st.text_input("You: ")
    if st.button("Send"):
        response = requests.post(
            "http://127.0.0.1:5000/chat",
            json={'message': user_input, 'session_name': st.session_state.selected_user}
        )
        st.write("Bot: " + response.json().get('response', 'Error'))
