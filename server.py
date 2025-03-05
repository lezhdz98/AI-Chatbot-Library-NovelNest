from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


app = Flask(__name__)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key = OPENAI_API_KEY,
    #organization= "Personal",
    #project="proj_oGAdo3IuZdMv3AMDUMK0HfVy"
)

#Creating assistant
# bot_assistant = client.beta.assistants.create(
#         name="Chatbot Assistant for a Library",
#         instructions='''You are an expert on the service customer side.
#         Use you knowledge base to answer questions about the business and to fitness topics always like a recomendation''',
#         model="gpt-4o",
#         tools=[{"type": "file_search"}],
#     )

# Store conversation history
conversation_history = [
    {
        "role":"system",
        "content":"You are a library chatbot support."
    }
]


@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    user_input = request.json.get('message')

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=conversation_history,
        max_tokens=150
    )

    response_str = response.choices[0].message.content
    
    # Add assistant response to conversation history
    conversation_history.append({"role": "assistant", "content": response_str})

    print(f"Chat History: \n{conversation_history}")
    
    return jsonify({'response': response_str})


if __name__ == '__main__':
    app.run(debug=True)
