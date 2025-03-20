import streamlit as st
import requests

st.title("Library Support Chatbot")

# Store session state
if "selected_user" not in st.session_state:
    st.session_state.selected_user = "(New User)"
if "existing_sessions" not in st.session_state:
    st.session_state.existing_sessions = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
st.session_state.new_user = ""

# Fetch existing sessions with error handling
def fetch_sessions():
    try:
        response = requests.get("http://127.0.0.1:5000/sessions")
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)
        if response.status_code == 200:
            st.session_state.existing_sessions = response.json().get("sessions", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sessions: {e}")


# Fetch chat history for the selected session
def fetch_chat_history(session_name):
    st.session_state.chat_history = ""
    try:
        response = requests.get(f"http://127.0.0.1:5000/chat_history?session_name={session_name}")
        response.raise_for_status()
        if response.status_code == 200:
            history = response.json().get("chat_history", [])
            st.session_state.chat_history = "\n".join(
                [f"{msg['role'].capitalize()}: {msg['content']}" for msg in history]
            )
    except requests.exceptions.RequestException as e:
        st.session_state.chat_history = "Error loading chat history."
        st.error(f"Error fetching chat history: {e}")

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
        fetch_chat_history(selected_user)  # Fetch chat history when session is selected
    elif new_user:
        # Check if new_user already exists in the existing sessions
        if new_user in st.session_state.existing_sessions:
            st.warning(f"The session name '{new_user}' already exists. Please choose a different name.")
        else:
            try:
                response = requests.post("http://127.0.0.1:5000/new_session", json={'session_name': new_user})
                response.raise_for_status()  # Raise an exception for HTTP errors
                if response.status_code == 200:
                    st.session_state.selected_user = new_user  # Auto-select new session
                    fetch_sessions()  # Refresh the dropdown
                    st.success(response.json()["message"])
                    st.rerun()  # Force a rerun to reflect the new session in the UI
                else:
                    st.error("Failed to create session.")
            except requests.exceptions.RequestException as e:
                st.error(f"Error creating new session: {e}")
    else:
        st.warning("Please select an existing session or enter a new name.")




# Chat input (only when a session is selected and user is not creating a new session)
if st.session_state.selected_user != "(New User)" and selected_user != "(New User)":
    fetch_chat_history(selected_user) 
    # Chat history
    st.text_area("Chat History", value=st.session_state.chat_history, height=250, disabled=True)

    user_input = st.text_input("You: ")
    
    if st.button("Send"):
        if user_input.strip():  # Check if input is not empty
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/chat",
                    json={'message': user_input, 'session_name': st.session_state.selected_user}
                )
                response.raise_for_status()  # Raise an exception for HTTP errors
                bot_response = response.json().get('response', 'Error')
                st.write("Bot: " + bot_response)

                # Update chat history in session state
                st.session_state.chat_history += f"\nYou: {user_input}\nBot: {bot_response}"
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error communicating with the chatbot backend: {e}")
           
            # Refresh UI
            st.rerun()
        else:
            st.warning("Please enter a message.")

   