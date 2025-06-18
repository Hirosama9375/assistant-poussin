
from flask import Flask, render_template_string, request, jsonify, send_file
import ollama
import os
import json
import time

from modules import chaos, blague, synthese, incoherence, planificateur, rapport, controle, style, humaniser, story, quiz, confess

app = Flask(__name__)

HISTORY_FILE = 'history.json'
os.makedirs('uploads', exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

POUSSIN_STATE = {
    "mode": "IA",   # IA ou ULTRA_HUMAIN
    "current_module": None
}

HTML = '''TON_HTML_REEL_ICI'''

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
    if POUSSIN_STATE["mode"] == "IA":
        POUSSIN_STATE["mode"] = "ULTRA HUMAIN"
    else:
        POUSSIN_STATE["mode"] = "IA"
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
        reply = chaos.run()
    elif mod == "blague":
        reply = blague.run()
    elif mod == "synthese":
        reply = synthese.run()
    elif mod == "incoherence":
        reply = incoherence.run()
    elif mod == "planificateur":
        reply = planificateur.run()
    elif mod == "rapport":
        reply = rapport.run()
    elif mod == "controle":
        reply = controle.run()
    elif mod == "style":
        reply = style.run()
    elif mod == "humaniser":
        reply = humaniser.run()
    elif mod == "story":
        reply = story.run()
    elif mod == "quiz":
        reply = quiz.run()
    elif mod == "confess":
        reply = confess.run()
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
