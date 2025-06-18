
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

HTML = '''
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <title>Assistant Poussin 🐣</title>
</head>
<body>
  <h1>Assistant Poussin 🐣</h1>
</body>
</html>
'''

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
        system = "Tu es Poussin ULTRA HUMAIN 🕵️‍♂️ : parle comme un humain normal."

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
    if mod == "chaos":
        reply = "[Module chaos] exécuté !"
    elif mod == "blague":
        reply = "[Module blague] Voici une blague."
    elif mod == "synthese":
        reply = "[Module synthese] Voici une synthèse."
    elif mod == "incoherence":
        reply = "[Module incoherence] Vérification incohérence."
    elif mod == "planificateur":
        reply = "[Module planificateur] Voici le planificateur."
    elif mod == "rapport":
        reply = "[Module rapport] Voici le rapport."
    elif mod == "controle":
        reply = "[Module controle] Contrôle effectué."
    elif mod == "style":
        reply = "[Module style] Style changé."
    elif mod == "humaniser":
        reply = "[Module humaniser] Texte humanisé."
    elif mod == "story":
        reply = "[Module story] Histoire générée."
    elif mod == "quiz":
        reply = "[Module quiz] Quiz lancé."
    elif mod == "confess":
        reply = "[Module confess] Confession traitée."
    else:
        reply = f"[Module {mod}] introuvable."
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
