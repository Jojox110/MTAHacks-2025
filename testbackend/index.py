from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama import Client

app = Flask(__name__)

# Allow CORS from localhost:8502
CORS(app, resources={r"/*": {"origins": "http://localhost:8502"}})

# Create Ollama client
ollama = Client(host="localhost:11434")

@app.route("/ollama", methods=["POST"])
def handle_ollama():
    # Get the JSON payload from the request
    data = request.get_json() or {}
    message = data.get("message", "")

    # Call ollama.chat with your model and user message
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": message, "format": 'json'}]
    )
    
    print(response.message.content)

    # Return the response as JSON
    return jsonify(response.message.content)

if __name__ == "__main__":
    # Run on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
