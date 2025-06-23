from flask import Flask, render_template_string, request, jsonify
import os, json, time
from openai import OpenAI

# === CONFIG ===
HISTORY_FILE = 'history.json'
EGG_COUNTER = 'poundometre.json'

# Liste avec GPT-3.5 Turbo et DALL·E-3
MODEL_LIST = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "dall-e-3"]

OPENAI_API_KEY = ""  # Mets ta clé API ici

client = OpenAI(api_key=OPENAI_API_KEY)

STATE = {
    "mode": "IA",
    "model": MODEL_LIST[0]
}

app = Flask(__name__)

# === INIT ===
for f, d in [(HISTORY_FILE, []), (EGG_COUNTER, {"total": 0})]:
    if not os.path.exists(f):
        json.dump(d, open(f, 'w'))

# === TON HTML (inchangé sauf typage) ===
HTML = '''
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <title>🐣 Poussin Révolution 🐣</title>
  <style>
    body { margin:0; font-family: Arial; display: flex; height: 100vh; background: #f4f4f4; }
    .sidebar {
      width: 260px; background: #27ae60; color: white; overflow-y: auto;
      padding: 20px; flex-shrink: 0; display: flex; flex-direction: column; align-items: center;
    }
    .sidebar img.logo { width: 100px; border-radius: 50%; animation: spin 8s linear infinite, pulse 2s infinite alternate; }
    @keyframes spin { from {transform: rotate(0);} to {transform: rotate(360deg);} }
    @keyframes pulse { from {transform: scale(1);} to {transform: scale(1.1);} }
    .sidebar button, .sidebar select {
      background: #2ecc71; color: white; border: none; margin: 5px 0; padding: 12px; border-radius: 8px; width: 100%; cursor: pointer;
      font-weight: bold; font-size: 14px;
    }
    .chat { flex: 1; padding: 20px; display: flex; flex-direction: column; overflow-y: auto; background: #fff; }
    .messages { flex: 1; overflow-y: auto; }
    .message { margin: 10px 0; padding: 10px 15px; border-radius: 15px; max-width: 70%; }
    .user { background: #d1f3d1; align-self: flex-end; }
    .assistant { background: #eee; align-self: flex-start; }
    .input-area { display: flex; margin-top: 20px; }
    .input-area input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 20px; }
    .input-area button { margin-left: 10px; padding: 10px 20px; border: none; background: #27ae60; color: white; border-radius: 20px; cursor: pointer; }
    #surprise { display: none; text-align: center; margin-top: 50px; }
    #surprise img { width: 300px; border-radius: 20px; margin: 10px; }
  </style>
</head>
<body>
  <div class="sidebar">
    <img class="logo" src="https://media.giphy.com/media/Y4z9olnoVl5QI/giphy.gif" alt="Poussin">
    <h3>Poussin 🐣</h3>
    <select id="modelSelect" onchange="changeModel()">
      {% for m in models %}
      <option value="{{m}}" {% if m == current_model %}selected{% endif %}>{{m}}</option>
      {% endfor %}
    </select>
    <button onclick="toggleMode()">Mode : <span id="modeLabel">{{mode}}</span></button>
    <hr>
    {% for mod in modules %}
    <button onclick="call('{{mod}}')">{{ modules[mod] }}</button>
    {% endfor %}
    <button onclick="surprise()">❤️ Mega Surprise pour Maman ❤️</button>
    <button onclick="clearChat()">🗑️ Effacer Chat</button>
  </div>
  <div class="chat">
    <div id="messages" class="messages"></div>
    <div id="typing"></div>
    <div class="input-area">
      <input id="msg" placeholder="Parle à Poussin...">
      <button onclick="send()">Envoyer</button>
    </div>
    <div id="surprise">
      <h2>💝 MAMAN JE T'AIME 💝</h2>
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Chicken_cartoon_04.svg/1024px-Chicken_cartoon_04.svg.png" alt="Poussin">
      <img src="https://images.unsplash.com/photo-1573329161113-7f539b71a6b7?ixlib=rb-4.0.3&auto=format&fit=crop&w=700&q=80" alt="Vachette">
      <p>Merci d'être la plus belle maman du monde 💕🐮🐣</p>
    </div>
  </div>
  <script>
    async function send() {
      const msg = document.getElementById('msg').value;
      if (!msg) return;
      add('user', msg);
      document.getElementById('msg').value = '';
      typing(true);
      const r = await fetch('/ask', {
        method:'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ message: msg })
      });
      const data = await r.json();
      typing(false);
      if (data.image) {
        add('assistant', "Image générée : <br><img src='" + data.image + "' width='400'>");
      } else {
        add('assistant', data.reply);
      }
    }
    function add(role, html) {
      const d = document.createElement('div');
      d.className = 'message ' + role;
      d.innerHTML = html;
      document.getElementById('messages').appendChild(d);
      document.getElementById('messages').scrollTop = 999999;
    }
    function typing(s) {
      document.getElementById('typing').innerText = s ? "🐱⏳ Génération en cours..." : "";
    }
    async function call(mod) {
      add('user', `[Module ${mod}]`);
      typing(true);
      const r = await fetch('/module/' + mod);
      const data = await r.json();
      typing(false);
      add('assistant', data.reply);
    }
    async function toggleMode() {
      const r = await fetch('/toggle_mode');
      const data = await r.json();
      document.getElementById('modeLabel').innerText = data.mode;
    }
    async function changeModel() {
      const val = document.getElementById('modelSelect').value;
      await fetch('/set_model', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({model: val})
      });
    }
    function surprise() {
      document.getElementById('messages').style.display = "none";
      document.getElementById('surprise').style.display = "block";
    }
    function clearChat() {
      document.getElementById('messages').innerHTML = '';
    }
  </script>
</body>
</html>
'''

# === ROUTES ===

@app.route('/')
def index():
    modules = {
        "Synthese": "📝 Synthèse",
        "Incoherence": "🤔 Incohérence",
        "Plan": "📋 Plan",
        "Rapport": "📑 Rapport",
        "Style": "🎭 Style",
        "Confession": "😳 Confession",
        "Blague": "😂 Blague",
        "Histoire": "📖 Histoire",
        "Quiz": "🧠 Quiz",
        "Chaos": "🌪️ Chaos",
        "Poeme": "📝 Poème",
        "Chant": "🎤 Chant",
        "Horoscope": "🔮 Horoscope",
        "Password": "🔑 Mot de passe",
        "Doux": "💌 Mot Doux",
        "Challenge": "🏆 Challenge",
        "Dodo": "💤 Dodo",
        "RendezVous": "📅 Rendez-vous",
        "PFC": "✊✋✌️ PFC",
        "MiniJeu": "🎮 Mini-Jeu",
        "Pondometre": "🥚 Pondomètre"
    }
    return render_template_string(HTML, mode=STATE["mode"], modules=modules, models=MODEL_LIST, current_model=STATE["model"])

@app.route('/ask', methods=['POST'])
def ask():
    d = request.json
    text = d['message'].lower()
    start_time = time.time()  # pour debug
    if STATE["model"] == "dall-e-3" or "génère une image" in text:
        prompt = text.replace("génère une image", "").strip()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        duration = time.time() - start_time
        print(f"[DALL·E] Durée de génération : {duration:.2f} sec")
        image_url = response.data[0].url
        return jsonify({"image": image_url})
    else:
        response = client.chat.completions.create(
            model=STATE["model"],
            messages=[
                {"role": "system", "content": "Tu es Poussin 🐣 une IA ultra gentille et révolutionnaire."},
                {"role": "user", "content": d['message']}
            ]
        )
        return jsonify({"reply": response.choices[0].message.content})

@app.route('/module/<mod>')
def module(mod):
    return jsonify({"reply": f"[Module {mod}] exécuté ! ✅"})

@app.route('/toggle_mode')
def toggle_mode():
    STATE["mode"] = "ULTRA HUMAIN" if STATE["mode"] == "IA" else "IA"
    return jsonify({"mode": STATE["mode"]})

@app.route('/set_model', methods=['POST'])
def set_model():
    d = request.json
    if d['model'] in MODEL_LIST:
        STATE["model"] = d['model']
    return '', 204

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
