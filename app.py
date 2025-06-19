
from flask import Flask, render_template_string, request, jsonify, send_file
import ollama
import os
import json
import time

app = Flask(__name__)

HISTORY_FILE = 'history.json'
os.makedirs('uploads', exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

POUSSIN_STATE = {
    "mode": "IA",
    "current_module": None
}

with open("interface.html") as f:
    HTML = f.read()

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data['message']
    temp = data.get('temp', 0.7)
    model = data.get('model', 'llama3:8b')

    if POUSSIN_STATE["mode"] == "IA":
        system = "Tu es Poussin GPT 🐣, assistant clair et structuré."
    else:
        system = "Tu es Poussin ULTRA HUMAIN 🕵️‍♂️."

    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_input}]
    response = ollama.chat(model=model, messages=messages, options={"temperature": temp})
    reply = response['message']['content']

    save_to_history(user_input, reply)
    return jsonify({"reply": reply})

@app.route('/toggle_mode')
def toggle_mode():
    POUSSIN_STATE["mode"] = "ULTRA HUMAIN" if POUSSIN_STATE["mode"] == "IA" else "IA"
    return jsonify({"mode": POUSSIN_STATE["mode"]})

@app.route('/export_txt')
def export_txt():
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    text = "\n\n".join([f"User: {h['user']}\nPoussin: {h['assistant']}" for h in history])
    with open('chat_export.txt', 'w') as f:
        f.write(text)
    return send_file('chat_export.txt', as_attachment=True)

@app.route('/clear_history')
def clear_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)
    return '', 204

@app.route('/module/<mod>')
def module(mod):
    replies = {
        "synthese": "Voici une synthèse 📚",
        "incoherence": "Vérifions les incohérences 🧐",
        "planificateur": "Planificateur activé 📅",
        "rapport": "Voici le rapport 📈",
        "controle": "Contrôle effectué 🔒",
        "style": "Style changé 🎭",
        "humaniser": "Réponse humanisée 🕵️‍♂️",
        "joke": "Voici une blague 😂",
        "story": "Voici une histoire 📚",
        "quiz": "Quiz lancé 🧠",
        "chaos": "Mode chaos activé 🌀",
        "confess": "Confession acceptée 😳"
    }
    reply = replies.get(mod, f"[Module {mod}] exécuté !")
    return jsonify({"reply": reply})

def save_to_history(user, assistant):
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    history.append({"user": user, "assistant": assistant, "time": time.time()})
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
