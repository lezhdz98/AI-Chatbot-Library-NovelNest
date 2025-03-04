from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(
    api_key = "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"
)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}],
        max_tokens=150
    )
    response_str = response.choices[0].message.content
    return jsonify({'response': response_str})

if __name__ == '__main__':
    app.run(debug=True)
