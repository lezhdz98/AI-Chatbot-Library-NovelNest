from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from faq_search_rag import query_faq_pinecone

load_dotenv()  # Load API key from .env

app = Flask(__name__)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#Store separate memory per user
session_memory = {}

#Define a function to get session history per user
def get_session_history(session_name: str):
    return session_memory[session_name].chat_memory.messages if session_name in session_memory else []

# AI-powered sentiment analysis
def analyze_sentiment(user_input):
    """Use OpenAI to analyze sentiment dynamically."""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    sentiment_prompt = f"Analyze the sentiment of this message and respond with either 'positive', 'neutral', or 'negative': {user_input}"
    
    response = llm.invoke(sentiment_prompt).content.strip().lower()
    return response  # Returns 'positive', 'neutral', or 'negative'

# AI-powered intent detection
def detect_intent(user_input):
    """Use OpenAI to classify user intent dynamically."""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    intent_prompt = (
        "Determine the intent of the following message and respond with one of these categories only:\n"
        "- appointment\n"
        "- escalation\n"
        "- general inquiry\n\n"
        "User Message: " + user_input + "\n\n"
        "Only return one of the categories without explanation."
    )

    response = llm.invoke(intent_prompt).content.strip().lower()
    return response  # Returns 'appointment', 'escalation', or 'general inquiry'

# Define a chat prompt template, initial prompt for the chatbot
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a friendly, professional, and knowledgeable library assistant. Your main task is to provide users with accurate and clear information about library services, including but not limited to:\n"
     "- Library hours and location\n"
     "- Membership registration, accounts, and borrowing policies\n"
     "- Library events, classes, and programs\n"
     "- Digital resources, technology, and facilities\n"
     "- Book donations, lost books, and other library policies\n\n"
     "Additionally, you can assist with the following actions:\n"
     "- **Appointment Booking**: Help users schedule study rooms, librarian consultations, event registrations, and book pickups.\n"
     "- **Escalation to a Librarian**: If a user has account issues, special requests, or serious complaints, escalate their request.\n"
     "- **Sentiment Analysis**: If a user seems frustrated or upset, offer extra support and escalate if needed.\n\n"
     "If the user asks for an appointment, confirm the type and acknowledge the booking.\n"
     "If the user expresses strong frustration or confusion, offer to escalate to a librarian.\n"
     "If you're unsure about something, ask for clarification or suggest the user contact library staff directly."),
    ("human", "{input}")
])

#Get all active sessions
@app.route('/sessions', methods=['GET'])
def get_sessions():
    return jsonify({"sessions": list(session_memory.keys())})

#Create a new session
@app.route('/new_session', methods=['POST'])
def new_session():
    session_name = request.json.get('session_name')
    if not session_name:
        return jsonify({"error": "Session name is required."}), 400

    if session_name not in session_memory:
        session_memory[session_name] = ConversationBufferMemory(return_messages=True)
        return jsonify({"message": f"Session '{session_name}' created successfully."})
    else:
        return jsonify({"message": f"Session '{session_name}' already exists."})

#Chat route with session handling
@app.route('/chat', methods=['POST'])
def chat():
    session_name = request.json.get('session_name')
    user_input = request.json.get('message')

    print(f"[User: {session_name}] {user_input}")

    if not session_name or session_name not in session_memory:
        return jsonify({'error': "Invalid session."}), 400

    # AI-powered sentiment detection
    sentiment = analyze_sentiment(user_input)
    if sentiment == "negative":
        print(f"[Mock] Escalating conversation due to negative sentiment in session {session_name}")
        return jsonify({'response': "I sense you're having trouble. I'll escalate this to a librarian for assistance."})

    # AI-powered intent detection
    detected_intent = detect_intent(user_input)
    if detected_intent == "appointment":
        print(f"[Mock] Booking an appointment for {session_name}")
        return jsonify({'response': "Your appointment has been scheduled!"})
    
    if detected_intent == "escalation":
        print(f"[Mock] Escalating issue for {session_name}")
        return jsonify({'response': "I'll escalate this to a librarian for further assistance."})


     # Query Pinecone (RAG part) to fetch relevant FAQ
    faq_answer = query_faq_pinecone(user_input)  # Call your RAG query function

    # Append the RAG result to the user's input before passing it to the LLM
    augmented_input = f"Here is a relevant FAQ I found: {faq_answer}\n\nUser's question: {user_input}"

    #Use OpenAI Model
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    #Get memory for the specific user session
    memory = session_memory[session_name]
    # Create a conversation chain with the augmented input
    chain = prompt | llm

    #Create a conversation object with the chain and memory
    conversation = RunnableWithMessageHistory(
        chain,
        memory=memory,
        #Pass the session history
        get_session_history=lambda session_id: session_memory[session_id].chat_memory 
        if session_id in session_memory else [] 
    )

    # Invoke the conversation with augmented input
    response = conversation.invoke(
        {"input": augmented_input},
        {"configurable": {"session_id": session_name}}
    )

    # Ensure the response is serializable and return
    response_content = response.content if hasattr(response, 'content') else str(response)

    # Ensure the response is serializable and return
    return jsonify({'response': response_content})

if __name__ == '__main__':
    app.run(debug=True)
