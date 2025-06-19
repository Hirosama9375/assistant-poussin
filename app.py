
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

HTML = "<h1>Assistant Poussin 🐣</h1><p>(Ton HTML complet ici)</p>"

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data['message']
    temp = data.get('temp', 0.7)
    model = data.get('model', 'llama3:8b')

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "Tu es Poussin GPT 🐣, assistant structuré." if POUSSIN_STATE["mode"] == "IA" else "Tu es Poussin ULTRA HUMAIN 🕵️‍♂️."},
            {"role": "user", "content": user_input}
        ],
        options={"temperature": temp},
        base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434")
    )
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

# ✅ MODULES internes
@app.route('/module/<mod>')
def module(mod):
    if mod == "chaos":
        reply = "Chaos total activé 🌀🤯 ! Prépare-toi !"
    elif mod == "joke":
        reply = "Pourquoi le poussin traverse la route ? Pour pondre un œuf de l'autre côté ! 😂"
    elif mod == "story":
        reply = "Il était une fois un poussin courageux qui pondait des idées... 🐣📚"
    elif mod == "quiz":
        reply = "Question Quiz : Combien de plumes a un poussin ? 🧠"
    elif mod == "confess":
        reply = "Je te confesse : Poussin adore tes questions ! 😳"
    else:
        reply = f"[Module {mod}] exécuté !"
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
