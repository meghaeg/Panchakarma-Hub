# backend/server.py
import os
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"


app = Flask(__name__)

def get_groq_response(messages, temperature=0.5):
    if not GROQ_API_KEY:
        return {"error": "Missing GROQ API Key"}

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": f"Groq API Error: {response.text}"}

    data = response.json()
    return {"reply": data["choices"][0]["message"]["content"]}

# Flask route for chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    temperature = data.get("temperature", 0.5)

    reply = get_groq_response(messages, temperature)
    return jsonify(reply)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
