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
                <li><strong>120 tokens</strong> → Squirrel Cheeks 🐿️ (10s)</li>
                <li><strong>130 tokens</strong> → Alien Face 👽 (10s)</li>
                <li><strong>140 tokens</strong> → Big Mouth 👄 (10s)</li>
                <li><strong>150 tokens</strong> → Pinocchio 🤥 (10s)</li>
                <li><strong>160 tokens</strong> → Sharp Chin 🔪 (10s)</li>
                <li><strong>170 tokens</strong> → Giant Forehead 🧠 (10s)</li>
                <li><strong>180 tokens</strong> → Cube Head 🧊 (10s)</li>
                <li><strong>190 tokens</strong> → Melted Face 🫠 (10s)</li>
                <li><strong>200 tokens</strong> → Snail eyes 🐌 (10s)</li>
                <li><strong>210 tokens</strong> → Permanent Smile 😬 (10s)</li>
                <li><strong>220 tokens</strong> → Big Eyes (10s)</li>
                <li><strong>230 tokens</strong> → Rabbit Ears 🐰 (10s)</li>
                <li><strong>240 tokens</strong> → Cyber Mask (10s)</li>
            </ul>
            
            <div class="test-links">
                <h3>🧪 Link-uri de Testare Rapidă</h3>
                <p><strong>Chaturbate:</strong></p>
                <ul>
                    
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/120/TestUser2', 'Chaturbate: 120 tokens (Squirrel Cheeks 🐿️)')">120 tokens (Squirrel Cheeks 🐿️)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/130/TestUser1', 'Chaturbate: 130 tokens (Alien Face 👽)')">130 tokens (Alien Face 👽)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/140/TestUser3', 'Chaturbate: 140 tokens (Big Mouth 👄)')">140 tokens (Big Mouth 👄)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/150/TestUser4', 'Chaturbate: 150 tokens (Pinocchio 🤥)')">150 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/160/TestUser9', 'Chaturbate: 160 tokens (Sharp Chin 🔪)')">160 tokens (Sharp Chin 🔪)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/170/TestUser10', 'Chaturbate: 200 tokens (Giant Forehead 🧠)')">170 tokens (Giant Forehead 🧠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/180/TestUser11', 'Chaturbate: 210 tokens (Cube Head 🧊)')">180 tokens (Cube Head 🧊)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/190/TestUser12', 'Chaturbate: 230 tokens (Melted Face 🫠)')">190 tokens (Melted Face 🫠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/200/TestUser13', 'Chaturbate: 240 tokens (Snail Eyes 🐌)')">200 tokens (Snail Eyes 🐌)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/210/TestUser14', 'Chaturbate: 250 tokens (Permanent Smile 😬)')">210 tokens (Permanent Smile 😬)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/220/TestUser15', 'Chaturbate: 260 tokens (Big Eyes)')">220 tokens (Big Eyes)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/230/TestUser16', 'Chaturbate: 270 tokens (Rabbit Ears 🐰)')">230 tokens (Rabbit Ears 🐰)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/chaturbate/240/TestUser17', 'Chaturbate: 280 tokens (Cyber Mask)')">240 tokens (Cyber Mask)</a></li>
                </ul>
                
                <p><strong>Stripchat:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/120/StripUser2', 'Stripchat: 120 tokens (Squirrel Cheeks 🐿️)')">120 tokens (Squirrel Cheeks 🐿️)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/130/StripUser1', 'Stripchat: 130 tokens (Alien Face 👽)')">130 tokens (Alien Face 👽)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/140/StripUser3', 'Stripchat: 140 tokens (Big Mouth 👄)')">140 tokens (Big Mouth 👄)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/150/StripUser4', 'Stripchat: 150 tokens (Pinocchio 🤥)')">150 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/160/StripUser9', 'Stripchat: 160 tokens (Sharp Chin 🔪)')">160 tokens (Sharp Chin 🔪)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/170/StripUser10', 'Stripchat: 170 tokens (Giant Forehead 🧠)')">170 tokens (Giant Forehead 🧠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/180/StripUser11', 'Stripchat: 180 tokens (Cube Head 🧊)')">180 tokens (Cube Head 🧊)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/190/StripUser12', 'Stripchat: 190 tokens (Melted Face 🫠)')">190 tokens (Melted Face 🫠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/200/StripUser13', 'Stripchat: 200 tokens (Snail Eyes 🐌)')">200 tokens (Snail Eyes 🐌)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/210/StripUser14', 'Stripchat: 210 tokens (Permanent Smile 😬)')">210 tokens (Permanent Smile 😬)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/220/StripUser15', 'Stripchat: 220 tokens (Big Eyes)')">220 tokens (Big Eyes)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/230 /StripUser16', 'Stripchat: 230 tokens (Rabbit Ears 🐰)')">230 tokens (Rabbit Ears 🐰)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/stripchat/240/StripUser17', 'Stripchat: 240 tokens (Cyber Mask)')">240 tokens (Cyber Mask)</a></li>
                    
                    
                </ul>
                
                <p><strong>Camsoda:</strong></p>
                <ul>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/120/CamUser2', 'Camsoda: 120 tokens (Squirrel Cheeks 🐿️)')">120 tokens (Squirrel Cheeks 🐿️)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/130/CamUser1', 'Camsoda: 130 tokens (Alien Face 👽)')">130 tokens (Alien Face 👽)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/140/CamUser3', 'Camsoda: 140 tokens (Big Mouth 👄)')">140 tokens (Big Mouth 👄)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/150/CamUser4', 'Camsoda: 150 tokens (Pinocchio 🤥)')">150 tokens (Pinocchio 🤥)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/160/CamUser9', 'Camsoda: 160 tokens (Sharp Chin 🔪)')">160 tokens (Sharp Chin 🔪)</a></li>    
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/170/CamUser10', 'Camsoda: 170 tokens (Giant Forehead 🧠)')">170 tokens (Giant Forehead 🧠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/180/CamUser11', 'Camsoda: 180 tokens (Cube Head 🧊)')">180 tokens (Cube Head 🧊)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/190/CamUser12', 'Camsoda: 190 tokens (Melted Face 🫠)')">190 tokens (Melted Face 🫠)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/200/CamUser13', 'Camsoda: 200 tokens (Snail Eyes 🐌)')">200 tokens (Snail Eyes 🐌)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/210/CamUser14', 'Camsoda: 210 tokens (Permanent Smile 😬)')">210 tokens (Permanent Smile 😬)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/220/CamUser15', 'Camsoda: 220 tokens (Big Eyes)')">220 tokens (Big Eyes)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/230 /CamUser16', 'Camsoda: 230 tokens (Rabbit Ears 🐰)')">230 tokens (Rabbit Ears 🐰)</a></li>
                    <li><a href="#" onclick="return sendTip('/trigger/camsoda/240/CamUser17', 'Camsoda: 240 tokens (Cyber Mask)')">240 tokens (Cyber Mask)</a></li>
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

