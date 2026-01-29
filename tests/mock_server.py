from flask import Flask, jsonify, request

app = Flask(__name__)

# Global variables to hold pending tips per platform
pending_tips = {
    'chaturbate': [],
    'stripchat': [],
    'camsoda': []
}


# =====================================
# CHATURBATE ENDPOINTS
# =====================================
@app.route('/trigger/chaturbate/<int:amount>/<string:user>', methods=['GET'])
def trigger_chaturbate(amount, user):
    """Simulează un tip de pe Chaturbate"""
    pending_tips['chaturbate'].append({
        "method": "tip",
        "object": {
            "amount": amount,
            "user": {
                "username": user
            }
        }
    })
    return f"✅ Chaturbate tip: {amount} tokens from {user}!"


@app.route('/events/chaturbate')
def get_chaturbate_events():
    """Returnează events Chaturbate"""
    events = pending_tips['chaturbate'].copy()
    pending_tips['chaturbate'].clear()  # Clear after sending
    
    return jsonify({
        "events": events,
        "next_url": "http://127.0.0.1:5000/events/chaturbate"
    })


# =====================================
# STRIPCHAT ENDPOINTS
# =====================================
@app.route('/trigger/stripchat/<int:amount>/<string:user>', methods=['GET'])
def trigger_stripchat(amount, user):
    """Simulează un tip de pe Stripchat"""
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
    """Returnează events Stripchat"""
    events = pending_tips['stripchat'].copy()
    pending_tips['stripchat'].clear()  # Clear after sending
    
    return jsonify({
        "events": events,
        "next_url": "http://127.0.0.1:5000/events/stripchat"
    })


# =====================================
# CAMSODA ENDPOINTS
# =====================================
@app.route('/trigger/camsoda/<int:amount>/<string:user>', methods=['GET'])
def trigger_camsoda(amount, user):
    """Simulează un tip de pe Camsoda"""
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
    """Returnează events Camsoda"""
    events = pending_tips['camsoda'].copy()
    pending_tips['camsoda'].clear()  # Clear after sending
    
    return jsonify({
        "events": events,
        "next_url": "http://127.0.0.1:5000/events/camsoda"
    })


# =====================================
# HOMEPAGE / DOCUMENTATION
# =====================================
@app.route('/')
def home():
    """Afișează documentația API-ului de testare"""
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
                <li><strong>27 tokens</strong> → Alien Face 👽 (12s)</li>
                <li><strong>32 tokens</strong> → Squirrel Cheeks 🐿️ (13s)</li>
                <li><strong>37 tokens</strong> → Big Mouth 👄 (14s)</li>
                <li><strong>43 tokens</strong> → Pinocchio 🤥 (30s)</li>
                <li><strong>46 tokens</strong> → Sharp Chin 🔪 (20s)</li>
                <li><strong>33 tokens</strong> → Sparkles (10s)</li>
                <li><strong>50 tokens</strong> → Rabbit Ears 🐰 (15s)</li>
                <li><strong>99 tokens</strong> → Big Eyes (20s)</li>
                <li><strong>200 tokens</strong> → Cyber Mask (30s)</li>
            </ul>
            
            <div class="test-links">
                <h3>🧪 Link-uri de Testare Rapidă</h3>
                <p><strong>Chaturbate:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/27/TestUser1', 'Chaturbate: 27 tokens (Alien Face 👽)')">27 tokens (Alien Face 👽)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/32/TestUser2', 'Chaturbate: 32 tokens (Squirrel Cheeks 🐿️)')">32 tokens (Squirrel Cheeks 🐿️)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/37/TestUser3', 'Chaturbate: 37 tokens (Big Mouth 👄)')">37 tokens (Big Mouth 👄)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/43/TestUser4', 'Chaturbate: 43 tokens (Pinocchio 🤥)')">43 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/46/TestUser9', 'Chaturbate: 46 tokens (Sharp Chin 🔪)')">46 tokens (Sharp Chin 🔪)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/33/TestUser5', 'Chaturbate: 33 tokens (Sparkles)')">33 tokens (Sparkles)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/50/TestUser6', 'Chaturbate: 50 tokens (Rabbit Ears 🐰)')">50 tokens (Rabbit Ears 🐰)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/99/TestUser7', 'Chaturbate: 99 tokens (Big Eyes)')">99 tokens (Big Eyes)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/200/TestUser8', 'Chaturbate: 200 tokens (Cyber Mask)')">200 tokens (Cyber Mask)</a></li>
                </ul>
                
                <p><strong>Stripchat:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/27/StripUser1', 'Stripchat: 27 tokens (Alien Face 👽)')">27 tokens (Alien Face 👽)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/32/StripUser2', 'Stripchat: 32 tokens (Squirrel Cheeks 🐿️)')">32 tokens (Squirrel Cheeks 🐿️)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/37/StripUser3', 'Stripchat: 37 tokens (Big Mouth 👄)')">37 tokens (Big Mouth 👄)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/43/StripUser4', 'Stripchat: 43 tokens (Pinocchio 🤥)')">43 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/46/StripUser9', 'Stripchat: 46 tokens (Sharp Chin 🔪)')">46 tokens (Sharp Chin 🔪)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/33/StripUser5', 'Stripchat: 33 tokens (Sparkles)')">33 tokens (Sparkles)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/50/StripUser6', 'Stripchat: 50 tokens (Rabbit Ears 🐰)')">50 tokens (Rabbit Ears 🐰)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/99/StripUser7', 'Stripchat: 99 tokens (Big Eyes)')">99 tokens (Big Eyes)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/200/StripUser8', 'Stripchat: 200 tokens (Cyber Mask)')">200 tokens (Cyber Mask)</a></li>
                </ul>
                
                <p><strong>Camsoda:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/27/CamUser1', 'Camsoda: 27 tokens (Alien Face 👽)')">27 tokens (Alien Face 👽)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/32/CamUser2', 'Camsoda: 32 tokens (Squirrel Cheeks 🐿️)')">32 tokens (Squirrel Cheeks 🐿️)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/37/CamUser3', 'Camsoda: 37 tokens (Big Mouth 👄)')">37 tokens (Big Mouth 👄)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/43/CamUser4', 'Camsoda: 43 tokens (Pinocchio 🤥)')">43 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/46/CamUser9', 'Camsoda: 46 tokens (Sharp Chin 🔪)')">46 tokens (Sharp Chin 🔪)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/33/CamUser5', 'Camsoda: 33 tokens (Sparkles)')">33 tokens (Sparkles)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/50/CamUser6', 'Camsoda: 50 tokens (Rabbit Ears 🐰)')">50 tokens (Rabbit Ears 🐰)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/99/CamUser7', 'Camsoda: 99 tokens (Big Eyes)')">99 tokens (Big Eyes)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/200/CamUser8', 'Camsoda: 200 tokens (Cyber Mask)')">200 tokens (Cyber Mask)</a></li>
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
    print("=" * 60)
    print("🚀 AR Filter System - Mock API Server")
    print("=" * 60)
    print("\n📡 Platforme disponibile:")
    print("   • Chaturbate: http://127.0.0.1:5000/events/chaturbate")
    print("   • Stripchat:  http://127.0.0.1:5000/events/stripchat")
    print("   • Camsoda:    http://127.0.0.1:5000/events/camsoda")
    print("\n🌐 Deschide http://127.0.0.1:5000 pentru documentație")
    print("=" * 60 + "\n")
    
    app.run(port=5000, debug=False)

