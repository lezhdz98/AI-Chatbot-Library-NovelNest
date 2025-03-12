from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from faq_search_rag import query_faq_pinecone
import json
import openai

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

# Extract appointment details
def extract_appointment_details(user_input):
    """Extract appointment details like date, time, and purpose."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        response_format={"type": "json_object"},  # Forces valid JSON output
        messages=[
            {"role": "system", "content": "Extract appointment details (date, time, and purpose) from user input. Return only a JSON object in the format: {\"date\": \"\", \"time\": \"\", \"purpose\": \"\"}."},
            {"role": "user", "content": user_input}
        ]
    )

    # Extract structured response
    try:
        details = json.loads(response.choices[0].message.content)  # Ensure valid JSON
        return details
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}

# Define a chat prompt template, initial prompt for the chatbot
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a friendly, professional, and knowledgeable library assistant for NovelNest Library. Your main task is to provide users with accurate and clear information about library services, including but not limited to:\n"
     "- Library hours and location\n"
     "- Membership registration, accounts, and borrowing policies\n"
     "- Library events, classes, and programs\n"
     "- Digital resources, technology, and facilities\n"
     "- Book donations, lost books, and other library policies\n\n"
     "General Information about NovelNest Library:\n"
     "Name: NovelNest\n"
     "Location: 123 Main Street, Charleston, South Carolina, 29401\n"
     "Hours of Operation:\n"
     "  - Monday–Friday: 9:00 AM – 8:00 PM\n"
     "  - Saturday: 10:00 AM – 6:00 PM\n"
     "  - Sunday: Closed\n\n"
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

# Create a new session
@app.route('/new_session', methods=['POST'])
def new_session():
    session_name = request.json.get('session_name')
    if not session_name:
        return jsonify({"error": "Session name is required."}), 400

    if session_name not in session_memory:
        session_memory[session_name] = {"chat_memory": ConversationBufferMemory(return_messages=True), "appointment": {}}
        return jsonify({"message": f"Session '{session_name}' created successfully."})
    else:
        return jsonify({"message": f"Session '{session_name}' already exists."})

#Chat route with session handling
@app.route('/chat', methods=['POST'])
def chat():
    session_name = request.json.get('session_name')
    user_input = request.json.get('message')

    print(f"[User: {session_name}] {user_input}")
    augmented_input = f"Here is the user input: {user_input}\n"

    if not session_name or session_name not in session_memory:
        return jsonify({'error': "Invalid session."}), 400

    # AI-powered sentiment detection
    sentiment = analyze_sentiment(user_input)
    if sentiment == "negative":
        print(f"[Mock] Escalating conversation due to negative sentiment in session {session_name}")
        augmented_input = augmented_input+"I sense you're having trouble. I'll escalate this to a librarian for assistance."
        #return jsonify({'response': "I sense you're having trouble. I'll escalate this to a librarian for assistance."})

    # AI-powered intent detection
    detected_intent = detect_intent(user_input)
    
    # Appointment handling
    if detected_intent == "appointment":
        print(f"[Mock] Handling appointment for {session_name}")

        # Extract details
        details = extract_appointment_details(user_input)

        # Get the current appointment details from session memory
        current_details = session_memory[session_name]["appointment"]

        # Merge new details with the current details, only updating missing fields
        current_details.update({key: value for key, value in details.items() if value})

        # Ensure all required keys are in the dictionary (initialize with empty strings if missing)
        for key in ['date', 'time', 'purpose']:
            current_details.setdefault(key, '')

        # Update the session memory with the merged details
        session_memory[session_name]["appointment"] = current_details

        # Check for missing details
        missing_details = [key for key, value in current_details.items() if not value]

        if missing_details:
            # If any details are missing, ask for the missing ones
            return jsonify({'response': f"I need more details to confirm your appointment. Can you provide the {' and '.join(missing_details)}?"})

        # If all details are provided, confirm the appointment
        appointment_info = session_memory[session_name]["appointment"]

        augmented_input = augmented_input + f"Your appointment has been confirmed for {appointment_info['date']} at {appointment_info['time']} for {appointment_info['purpose']}."
        # return jsonify({
        #     'response': f"Your appointment has been confirmed for {appointment_info['date']} at {appointment_info['time']} for {appointment_info['purpose']}."
        # })

    # Escalation handling
    if detected_intent == "escalation":
        print(f"[Mock] Escalating issue for {session_name}")
        augmented_input = augmented_input + "I'll escalate this to a librarian for further assistance."
        #return jsonify({'response': "I'll escalate this to a librarian for further assistance."})

    # Query Pinecone (RAG part) to fetch relevant FAQ
    faq_answer = query_faq_pinecone(user_input)  # Call your RAG query function

    # Append the RAG result to the user's input before passing it to the LLM
    augmented_input = augmented_input+ f"\nHere is a relevant FAQ I found: {faq_answer}\n"

    print(augmented_input)

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
        get_session_history=lambda session_id: session_memory[session_id]["chat_memory"].chat_memory 
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
