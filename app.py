
from flask import Flask, render_template_string, request, jsonify
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
  <style>
    body { margin:0; display:flex; height:100vh; font-family: Arial, sans-serif; }
    .sidebar { width:260px; background:#f9f9f9; padding:20px; }
    .chat-container { flex:1; display:flex; flex-direction:column; }
    .messages { flex:1; padding:20px; overflow-y:auto; }
    .message { margin:10px 0; padding:12px; border-radius:18px; }
    .user { background:#d1f3d1; align-self:flex-end; }
    .assistant { background:#f0f0f0; align-self:flex-start; }
    .input-area { display:flex; padding:10px; background:#fafafa; }
    .input-area input { flex:1; padding:12px; }
    .input-area button { margin-left:10px; padding:10px 20px; }
  </style>
</head>
<body>
  <div class="sidebar">
    <h3>Assistant Poussin 🐣</h3>
    <button onclick="callModule('synthese')">Synthèse 📚</button>
    <button onclick="callModule('incoherence')">Incohérence 🧐</button>
    <button onclick="callModule('planificateur')">Planificateur 📅</button>
    <button onclick="callModule('rapport')">Rapport 📈</button>
    <button onclick="callModule('controle')">Contrôle 🔒</button>
    <button onclick="callModule('style')">Changer Style 🎭</button>
    <button onclick="callModule('humaniser')">Humaniser 🕵️‍♂️</button>
    <button onclick="callModule('joke')">Blague 😂</button>
    <button onclick="callModule('story')">Histoire 📚</button>
    <button onclick="callModule('quiz')">Quiz 🧠</button>
    <button onclick="callModule('chaos')">Chaos 🌀</button>
    <button onclick="callModule('confess')">Confession 😳</button>
  </div>
  <div class="chat-container">
    <div class="messages" id="messages"></div>
    <div class="input-area">
      <input id="msg" placeholder="Parle à Poussin...">
      <button onclick="sendText()">Envoyer</button>
    </div>
  </div>
<script>
async function sendText() {
  const msg = document.getElementById('msg').value.trim();
  if (!msg) return;
  addMessage('user', msg);
  document.getElementById('msg').value = '';
  const res = await fetch('/ask', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message: msg})});
  const data = await res.json();
  addMessage('assistant', data.reply);
}
function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = 'message ' + role;
  div.innerText = text;
  document.getElementById('messages').appendChild(div);
}
async function callModule(mod) {
  addMessage('user', `[Module ${mod}]`);
  const res = await fetch('/module/' + mod);
  const data = await res.json();
  addMessage('assistant', data.reply);
}
</script>
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
    messages = [{"role": "system", "content": "Assistant Poussin 🐣"}, {"role": "user", "content": user_input}]
    reply = f"Réponse simulée pour: {user_input}"
    return jsonify({"reply": reply})

@app.route('/module/<mod>')
def module(mod):
    return jsonify({"reply": f"Module {mod} exécuté !"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
