"""
Mock Server pentru testarea sistemului de filtre
Simuleaza API-urile platformelor (Chaturbate, Stripchat, Camsoda)
Permite testarea fara a avea cont real sau acces la API-uri de productie
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

# Variabile globale pentru stocarea temporara a tip-urilor simulate pe fiecare platforma
pending_tips = {
    'chaturbate': [],  # Lista de tip-uri Chaturbate in asteptare
    'stripchat': [],   # Lista de tip-uri Stripchat in asteptare
    'camsoda': []      # Lista de tip-uri Camsoda in asteptare
}


# =====================================
# CHATURBATE ENDPOINTS
# =====================================
@app.route('/trigger/chaturbate/<int:amount>/<string:user>', methods=['GET'])
def trigger_chaturbate(amount, user):
    """
    Endpoint pentru simularea unui tip pe Chaturbate
    Accesibil prin browser pentru testare rapida
    
    Args:
        amount: Suma de tokeni (int)
        user: Numele utilizatorului care da tip (string)
    
    Returns:
        Mesaj de confirmare
    """
    # Creeaza un eveniment in formatul Chaturbate Events API
    pending_tips['chaturbate'].append({
        "broadcaster": "test_broadcaster",
        "tip": {
            "tokens": amount,
            "isAnon": False,
            "message": "Test tip from mock server"
        },
        "user": {
            "username": user,
            "inFanclub": False,
            "gender": "m",
            "hasTokens": True,
            "recentTips": "none",
            "isMod": False
        }
    })
    return f"✅ Chaturbate tip: {amount} tokens from {user}!"


@app.route('/events/chaturbate')
def get_chaturbate_events():
    """
    Endpoint care simuleaza Chaturbate Events API
    Returneaza toate evenimentele in asteptare si le sterge
    """
    # Copiaza evenimentele curente
    events = pending_tips['chaturbate'].copy()
    # Sterge evenimentele dupa trimitere (simulate "consumed")
    pending_tips['chaturbate'].clear()
    
    return jsonify({
        "events": events,
        "next_url": "http://127.0.0.1:5000/events/chaturbate"
    })


# =====================================
# STRIPCHAT ENDPOINTS
# =====================================
@app.route('/trigger/stripchat/<int:amount>/<string:user>', methods=['GET'])
def trigger_stripchat(amount, user):
    """
    Endpoint pentru simularea unui tip pe Stripchat
    Accesibil prin browser pentru testare rapida
    
    Args:
        amount: Suma de tokeni (int)
        user: Numele utilizatorului care da tip (string)
    
    Returns:
        Mesaj de confirmare
    """
    # Creeaza un eveniment in formatul Stripchat Events API
    pending_tips['stripchat'].append({
        "type": "tip",
        "data": {
            "tokens": amount,
            "from": {
                "username": user
            }
        }
    })
    return f"✅ Stripchat tip: {amount} tokens from {user}!"


@app.route('/events/stripchat')
def get_stripchat_events():
    """
    Endpoint care simuleaza Stripchat Events API
    Returneaza toate evenimentele in asteptare si le sterge
    """
    # Copiaza evenimentele curente
    events = pending_tips['stripchat'].copy()
    # Sterge evenimentele dupa trimitere
    pending_tips['stripchat'].clear()
    
    return jsonify({
        "events": events,
        "next_url": "http://127.0.0.1:5000/events/stripchat"
    })


# =====================================
# CAMSODA ENDPOINTS
# =====================================
@app.route('/trigger/camsoda/<int:amount>/<string:user>', methods=['GET'])
def trigger_camsoda(amount, user):
    """
    Endpoint pentru simularea unui tip pe Camsoda
    Accesibil prin browser pentru testare rapida
    
    Args:
        amount: Suma de tokeni (int)
        user: Numele utilizatorului care da tip (string)
    
    Returns:
        Mesaj de confirmare
    """
    # Creeaza un eveniment in formatul Camsoda External API
    pending_tips['camsoda'].append({
        "event_type": "tip",
        "tip_amount": amount,
        "tipper": {
            "name": user
        }
    })
    return f"✅ Camsoda tip: {amount} tokens from {user}!"


@app.route('/events/camsoda')
def get_camsoda_events():
    """
    Endpoint care simuleaza Camsoda External API
    Returneaza toate evenimentele in asteptare si le sterge
    """
    # Copiaza evenimentele curente
    events = pending_tips['camsoda'].copy()
    # Sterge evenimentele dupa trimitere
    pending_tips['camsoda'].clear()
    
    return jsonify({
        "events": events,
        "next_url": "http://127.0.0.1:5000/events/camsoda"
    })


# =====================================
# HOMEPAGE / DOCUMENTATION
# =====================================
@app.route('/')
def home():
    """
    Pagina principala cu documentatie interactiva
    Afiseaza toate endpoint-urile disponibile si exemple de utilizare
    Include linkuri clickabile pentru testare rapida
    """
    return """
    <html>
    <head>
        <title>AR Filter System - Mock API Server</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1000px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 { color: #FFD700; margin-top: 0; }
            h2 { color: #FFA500; border-bottom: 2px solid #FFA500; padding-bottom: 10px; }
            .endpoint {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #FFD700;
            }
            code {
                background: rgba(0, 0, 0, 0.5);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
            .platform {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 10px;
            }
            .chaturbate { background: #ff6b35; }
            .stripchat { background: #00d4ff; }
            .camsoda { background: #00ff88; }
            .test-links {
                background: rgba(255, 255, 255, 0.2);
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }
            a {
                color: #FFD700;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
                cursor: pointer;
            }
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0, 255, 136, 0.9);
                color: #000;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                animation: slideIn 0.3s ease-out;
                z-index: 1000;
            }
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        </style>
        <script>
            function sendTip(url, description) {
                // Send the request in the background
                fetch(url)
                    .then(response => response.text())
                    .then(data => {
                        showNotification(`✅ ${description}`);
                    })
                    .catch(error => {
                        showNotification(`❌ Error: ${error}`);
                    });
                
                // Prevent default link behavior
                return false;
            }
            
            function showNotification(message) {
                // Create notification element
                const notif = document.createElement('div');
                notif.className = 'notification';
                notif.textContent = message;
                document.body.appendChild(notif);
                
                // Remove after 3 seconds
                setTimeout(() => {
                    notif.style.opacity = '0';
                    notif.style.transform = 'translateX(400px)';
                    setTimeout(() => notif.remove(), 300);
                }, 3000);
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🎥 AR Filter System - Mock API Server</h1>
            <p>Server de testare pentru simularea tips-urilor de pe multiple platforme</p>
            
            <h2>📡 Platforme Disponibile</h2>
            
            <div class="endpoint">
                <span class="platform chaturbate">CHATURBATE</span>
                <p><strong>Trigger Tip:</strong> <code>GET /trigger/chaturbate/&lt;amount&gt;/&lt;username&gt;</code></p>
                <p><strong>Events Endpoint:</strong> <code>GET /events/chaturbate</code></p>
                <p><strong>Format JSON:</strong></p>
                <pre><code>{
  "method": "tip",
  "object": {
    "amount": 100,
    "user": {"username": "user123"}
  }
}</code></pre>
            </div>
            
            <div class="endpoint">
                <span class="platform stripchat">STRIPCHAT</span>
                <p><strong>Trigger Tip:</strong> <code>GET /trigger/stripchat/&lt;amount&gt;/&lt;username&gt;</code></p>
                <p><strong>Events Endpoint:</strong> <code>GET /events/stripchat</code></p>
                <p><strong>Format JSON:</strong></p>
                <pre><code>{
  "type": "tip",
  "data": {
    "tokens": 100,
    "from": {"username": "user123"}
  }
}</code></pre>
            </div>
            
            <div class="endpoint">
                <span class="platform camsoda">CAMSODA</span>
                <p><strong>Trigger Tip:</strong> <code>GET /trigger/camsoda/&lt;amount&gt;/&lt;username&gt;</code></p>
                <p><strong>Events Endpoint:</strong> <code>GET /events/camsoda</code></p>
                <p><strong>Format JSON:</strong></p>
                <pre><code>{
  "event_type": "tip",
  "tip_amount": 100,
  "tipper": {"name": "user123"}
}</code></pre>
            </div>
            
            <h2>🎯 Filtre Disponibile</h2>
            <ul>
                <li><strong>119 tokens</strong> → Cartoon Style 🎨 (10s)</li>
                <li><strong>129 tokens</strong> → Neon Devil 😈 (10s)</li>
                <li><strong>139 tokens</strong> → Shock ML ⚡ (10s)</li>
                <li><strong>149 tokens</strong> → Crying ML 😢 (10s)</li>
                <li><strong>159 tokens</strong> → Kisses 💋 (10s)</li>
                <li><strong>169 tokens</strong> → Pinocchio 🤥 (10s)</li>
                <li><strong>179 tokens</strong> → Ski Mask 🎿 (10s)</li>
                <li><strong>189 tokens</strong> → Cowboy 🤠 (10s)</li>
                <li><strong>199 tokens</strong> → Big Cheeks 😊 (10s)</li>
                <li><strong>209 tokens</strong> → Lips Morph 👄 (10s)</li>
            </ul>
            
            <div class="test-links">
                <h3>🧪 Link-uri de Testare Rapidă</h3>
                <p><strong>Chaturbate:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/119/TestUser1', 'Chaturbate: 119 tokens (Cartoon Style 🎨)')">119 tokens (Cartoon Style 🎨)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/129/TestUser2', 'Chaturbate: 129 tokens (Neon Devil 😈)')">129 tokens (Neon Devil 😈)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/139/TestUser3', 'Chaturbate: 139 tokens (Shock ML ⚡)')">139 tokens (Shock ML ⚡)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/149/TestUser4', 'Chaturbate: 149 tokens (Crying ML 😢)')">149 tokens (Crying ML 😢)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/159/TestUser5', 'Chaturbate: 159 tokens (Kisses 💋)')">159 tokens (Kisses 💋)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/169/TestUser6', 'Chaturbate: 169 tokens (Pinocchio 🤥)')">169 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/179/TestUser7', 'Chaturbate: 179 tokens (Ski Mask 🎿)')">179 tokens (Ski Mask 🎿)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/189/TestUser8', 'Chaturbate: 189 tokens (Cowboy 🤠)')">189 tokens (Cowboy 🤠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/199/TestUser9', 'Chaturbate: 199 tokens (Big Cheeks 😊)')">199 tokens (Big Cheeks 😊)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/209/TestUser10', 'Chaturbate: 209 tokens (Lips Morph 👄)')">209 tokens (Lips Morph 👄)</a></li>
                </ul>
                
                <p><strong>Stripchat:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/119/StripUser1', 'Stripchat: 119 tokens (Cartoon Style 🎨)')">119 tokens (Cartoon Style 🎨)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/129/StripUser2', 'Stripchat: 129 tokens (Neon Devil 😈)')">129 tokens (Neon Devil 😈)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/139/StripUser3', 'Stripchat: 139 tokens (Shock ML ⚡)')">139 tokens (Shock ML ⚡)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/149/StripUser4', 'Stripchat: 149 tokens (Crying ML 😢)')">149 tokens (Crying ML 😢)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/159/StripUser5', 'Stripchat: 159 tokens (Kisses 💋)')">159 tokens (Kisses 💋)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/169/StripUser6', 'Stripchat: 169 tokens (Pinocchio 🤥)')">169 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/179/StripUser7', 'Stripchat: 179 tokens (Ski Mask 🎿)')">179 tokens (Ski Mask 🎿)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/189/StripUser8', 'Stripchat: 189 tokens (Cowboy 🤠)')">189 tokens (Cowboy 🤠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/199/StripUser9', 'Stripchat: 199 tokens (Big Cheeks 😊)')">199 tokens (Big Cheeks 😊)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/209/StripUser10', 'Stripchat: 209 tokens (Lips Morph 👄)')">209 tokens (Lips Morph 👄)</a></li>
                </ul>
                
                <p><strong>Camsoda:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/119/CamUser1', 'Camsoda: 119 tokens (Cartoon Style 🎨)')">119 tokens (Cartoon Style 🎨)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/129/CamUser2', 'Camsoda: 129 tokens (Neon Devil 😈)')">129 tokens (Neon Devil 😈)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/139/CamUser3', 'Camsoda: 139 tokens (Shock ML ⚡)')">139 tokens (Shock ML ⚡)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/149/CamUser4', 'Camsoda: 149 tokens (Crying ML 😢)')">149 tokens (Crying ML 😢)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/159/CamUser5', 'Camsoda: 159 tokens (Kisses 💋)')">159 tokens (Kisses 💋)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/169/CamUser6', 'Camsoda: 169 tokens (Pinocchio 🤥)')">169 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/179/CamUser7', 'Camsoda: 179 tokens (Ski Mask 🎿)')">179 tokens (Ski Mask 🎿)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/189/CamUser8', 'Camsoda: 189 tokens (Cowboy 🤠)')">189 tokens (Cowboy 🤠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/199/CamUser9', 'Camsoda: 199 tokens (Big Cheeks 😊)')">199 tokens (Big Cheeks 😊)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/209/CamUser10', 'Camsoda: 209 tokens (Lips Morph 👄)')">209 tokens (Lips Morph 👄)</a></li>
                </ul>
            </div>
            
            <h2>💡 Cum se folosește</h2>
            <ol>
                <li>Pornește acest server: <code>python tests/mock_server.py</code></li>
                <li>Pornește aplicația principală: <code>python main.py</code></li>
                <li>Click pe link-urile de mai sus pentru a simula tips</li>
                <li>Observă filtrele activate în aplicația AR!</li>
            </ol>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    """
    Punct de intrare pentru Mock Server
    Afiseaza informatii despre endpoint-uri si porneste serverul Flask
    """
    print("=" * 60)
    print("🚀 AR Filter System - Mock API Server")
    print("=" * 60)
    print("\n📡 Platforme disponibile:")
    print("   • Chaturbate: http://127.0.0.1:5000/events/chaturbate")
    print("   • Stripchat:  http://127.0.0.1:5000/events/stripchat")
    print("   • Camsoda:    http://127.0.0.1:5000/events/camsoda")
    print("\n🌐 Deschide http://127.0.0.1:5000 pentru documentatie")
    print("=" * 60 + "\n")
    
    # Porneste serverul Flask pe portul 5000
    app.run(port=5000, debug=False)

