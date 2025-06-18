
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

POUSSIN_STATE = {"mode": "IA", "current_module": None}

HTML = '''
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <title>Assistant Poussin 🐣</title>
  <style>
    body { margin:0; display:flex; height:100vh; font-family: Arial, sans-serif; transition: background 0.3s; }
    body.dark { background:#222; color:white; }
    .sidebar {
      width:260px; background:#f9f9f9; border-right:1px solid #ddd;
      padding:20px; text-align:center; overflow-y:auto;
    }
    body.dark .sidebar { background:#333; color:white; }
    .sidebar img { width:80px; height:80px; border-radius:50%; }
    .sidebar button {
      width:100%; margin:5px 0; padding:10px;
      border:none; border-radius:8px; background:#4CAF50;
      color:white; cursor:pointer; font-weight:bold;
    }
    .sidebar select, .sidebar input[type=range], .sidebar input[type=color] {
      width:90%; margin:8px 0;
    }
    .chat-container { flex:1; display:flex; flex-direction:column; }
    .messages { flex:1; padding:20px; overflow-y:auto; display:flex; flex-direction:column; }
    .message {
      margin:10px 0; padding:12px 18px; border-radius:18px; max-width:70%;
      word-wrap:break-word; font-size:15px;
    }
    .user { background: var(--user-bubble, #d1f3d1); align-self:flex-end; }
    .assistant { background: #f0f0f0; align-self:flex-start; }
    body.dark .assistant { background:#444; color:white; }
    .input-area {
      display:flex; border-top:1px solid #ddd; padding:10px; background:#fafafa;
    }
    body.dark .input-area { background:#333; }
    .input-area input {
      flex:1; padding:12px; font-size:16px; border:1px solid #ccc; border-radius:20px;
    }
    .input-area button {
      margin-left:10px; padding:10px 20px; border:none; background:#4CAF50; color:white;
      border-radius:20px; cursor:pointer; font-weight:bold;
    }
    #typing { padding:5px; font-style:italic; }
  </style>
</head>
<body>
  <div class="sidebar">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Emoji_u1f614.svg/1024px-Emoji_u1f614.svg.png" alt="Poussin">
    <h3>Assistant Poussin 🐣</h3>
    <label>Modèle :</label><br>
    <select id="model">
      <option value="llama3:8b">Llama3 8B</option>
      <option value="mixtral:7b">Mixtral 7B</option>
    </select><br>
    <label>Créativité :</label><br>
    <input type="range" id="temp" min="0" max="1" step="0.1" value="0.3"><br>
    <label>Couleur Bulle User :</label><br>
    <input type="color" id="bubbleColor" value="#d1f3d1" onchange="changeBubbleColor()"><br>
    <button onclick="toggleDark()">🌙 / ☀️</button>
    <hr>
    <button onclick="toggleMode()">Mode : <span id="modeLabel">IA</span></button>
    <hr>
    <button onclick="callModule('synthese')">Synthèse 📚</button>
    <button onclick="callModule('incoherence')">Incohérence 🧐</button>
    <button onclick="callModule('planificateur')">Planificateur 📅</button>
    <button onclick="callModule('rapport')">Rapport 📈</button>
    <button onclick="callModule('controle')">Contrôle 🔒</button>
    <button onclick="callModule('style')">Changer Style 🎭</button>
    <button onclick="callModule('humaniser')">Humaniser 🕵️‍♂️</button>
    <hr>
    <button onclick="callModule('joke')">Blague 😂</button>
    <button onclick="callModule('story')">Histoire 📚</button>
    <button onclick="callModule('quiz')">Quiz 🧠</button>
    <button onclick="callModule('chaos')">Chaos 🌀</button>
    <button onclick="callModule('confess')">Confession 😳</button>
    <hr>
    <button onclick="exportTXT()">Exporter TXT</button>
    <button onclick="clearHistory()">🗑️ Effacer Chat</button>
  </div>

  <div class="chat-container">
    <div class="messages" id="messages"></div>
    <div id="typing"></div>
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
      typing(true);
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          message: msg,
          temp: parseFloat(document.getElementById('temp').value),
          model: document.getElementById('model').value
        })
      });
      const data = await res.json();
      typing(false);
      addMessage('assistant', data.reply);
    }
    function addMessage(role, text) {
      const div = document.createElement('div');
      div.className = 'message ' + role;
      div.innerText = text;
      document.getElementById('messages').appendChild(div);
      document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
    }
    function typing(status) {
      document.getElementById('typing').innerText = status ? "Poussin pond un œuf... 🐣⏳" : "";
    }
    function toggleDark() {
      document.body.classList.toggle('dark');
    }
    function changeBubbleColor() {
      document.body.style.setProperty('--user-bubble', document.getElementById('bubbleColor').value);
    }
    async function toggleMode() {
      const res = await fetch('/toggle_mode');
      const data = await res.json();
      document.getElementById('modeLabel').innerText = data.mode;
    }
    async function callModule(mod) {
      addMessage('user', `[Module ${mod}]`);
      typing(true);
      const res = await fetch('/module/' + mod);
      const data = await res.json();
      typing(false);
      addMessage('assistant', data.reply);
    }
    async function exportTXT() {
      window.open('/export_txt');
    }
    async function clearHistory() {
      await fetch('/clear_history');
      document.getElementById('messages').innerHTML = '';
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
    temp = float(data.get('temp', 0.3))
    model = data.get('model', 'llama3:8b')
    system = "Réponse courte." if POUSSIN_STATE["mode"] == "IA" else "Réponse courte, style humain."
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_input}]
    response = ollama.chat(model=model, messages=messages, options={"temperature": temp, "top_p": 0.7, "num_predict": 16})
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
    return jsonify({"reply": f"[Module {mod}] exécuté ✅"})

def save_to_history(user, assistant):
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    history.append({"user": user, "assistant": assistant, "time": time.time()})
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
