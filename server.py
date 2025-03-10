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

# Create a prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful library chatbot. Keep your responses clear and concise."),
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

    print(session_name, user_input)

    if not session_name or session_name not in session_memory:
        return jsonify({'error': "Invalid session."}), 400

    #Use OpenAI Model
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

    #Get memory for the specific user session
    memory = session_memory[session_name]

     # Query Pinecone (RAG part) to fetch relevant FAQ
    faq_answer = query_faq_pinecone(user_input)  # Call your RAG query function

    # Append the RAG result to the user's input before passing it to the LLM
    augmented_input = f"Here is a relevant FAQ I found: {faq_answer}\n\nUser's question: {user_input}"

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

    # Extracting the content from AIMessage
    if isinstance(response, list):
        # If response is a list of AIMessage objects, extract text content
        response_content = [message.content for message in response if hasattr(message, 'content')]
    else:
        # If it's a single message object, extract content
        response_content = response.content if hasattr(response, 'content') else str(response)

    # Ensure the response is serializable and return
    return jsonify({'response': response_content})

if __name__ == '__main__':
    app.run(debug=True)
