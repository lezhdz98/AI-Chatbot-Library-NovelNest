import streamlit as st
import requests

st.title("Gym Support Chatbot")

user_input = st.text_input("You: ")
if st.button("Send"):
    response = requests.post("http://127.0.0.1:5000/chat", json={'message': user_input})
    st.write("Bot: " + response.json()['response'])