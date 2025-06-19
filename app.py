
from flask import Flask, render_template, request, jsonify
import ollama
import json
import os
import time

app = Flask(__name__)

HISTORY_FILE = 'history.json'
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

POUSSIN_STATE = {"mode": "IA"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data['message']
    temp = data.get('temp', 0.7)
    model = data.get('model', 'llama3:8b')
    system = "Tu es Poussin GPT 🐣" if POUSSIN_STATE["mode"] == "IA" else "Tu es Poussin ULTRA HUMAIN 🕵️‍♂️"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_input}]
    response = ollama.chat(model=model, messages=messages, options={"temperature": temp})
    reply = response['message']['content']
    save_to_history(user_input, reply)
    return jsonify({"reply": reply})

@app.route('/toggle_mode')
def toggle_mode():
    POUSSIN_STATE["mode"] = "ULTRA HUMAIN" if POUSSIN_STATE["mode"] == "IA" else "IA"
    return jsonify({"mode": POUSSIN_STATE["mode"]})

@app.route('/module/<mod>')
def module(mod):
    responses = {
        "synthese": "Voici une synthèse 📚",
        "incoherence": "Vérification d'incohérence 🧐",
        "planificateur": "Planificateur activé 📅",
        "rapport": "Voici le rapport 📈",
        "controle": "Contrôle 🔒 effectué",
        "style": "Style changé 🎭",
        "humaniser": "Humanisation 🕵️‍♂️",
        "joke": "Une blague 😂 : Pourquoi le poussin traverse la route ?",
        "story": "Il était une fois un poussin... 📚",
        "quiz": "Voici un quiz 🧠",
        "chaos": "Mode Chaos 🌀",
        "confess": "Confession 😳"
    }
    reply = responses.get(mod, "Module inconnu")
    return jsonify({"reply": reply})

@app.route('/export_txt')
def export_txt():
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    text = "\n\n".join([f"User: {h['user']}\nPoussin: {h['assistant']}" for h in history])
    with open('chat_export.txt', 'w') as f:
        f.write(text)
    return jsonify({"status": "exported"})

@app.route('/clear_history')
def clear_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)
    return '', 204

def save_to_history(user, assistant):
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    history.append({"user": user, "assistant": assistant, "time": time.time()})
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
