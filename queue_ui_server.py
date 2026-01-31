"""
Queue UI Server - Server web pentru afisarea cozii de filtre in timp real
Folosit pentru integrare cu OBS (Open Broadcaster Software)
Furnizeaza 2 pagini: coada in timp real si meniul de filtre
"""
from flask import Flask, render_template, jsonify, Response
import json
import time
import threading
from collections import deque

app = Flask(__name__)

# Date globale pentru coada de filtre
queue_data = {
    "current_filter": None,  # Filtrul activ momentan
    "queue": deque(maxlen=50),  # Maxim 50 de elemente in coada
    "total_count": 0  # Numarul total de filtre in asteptare
}

# Lock pentru sincronizarea accesului la date (thread-safe)
queue_lock = threading.Lock()

# Lista conexiunilor SSE active (Server-Sent Events)
sse_connections = []


def add_to_queue(filter_name, username, amount):
    """
    Adauga un filtru nou in coada
    Daca nu exista filtru activ, seteaza primul ca fiind activ
    
    Args:
        filter_name: Numele filtrului (ex: "Cartoon Style")
        username: Numele utilizatorului care a dat tip
        amount: Suma de tokeni
    """
    with queue_lock:
        # Adauga noul item in coada
        queue_data["queue"].append({
            "filter": filter_name,
            "username": username,
            "amount": amount,
            "timestamp": time.time()
        })
        
        # Daca nu exista filtru activ, seteaza primul din coada ca activ (FARA a-l sterge)
        if queue_data["current_filter"] is None and len(queue_data["queue"]) > 0:
            queue_data["current_filter"] = queue_data["queue"][0]
        
        queue_data["total_count"] = len(queue_data["queue"])
    
    # Notifica toate conexiunile SSE despre modificare
    broadcast_update()


def next_filter():
    """
    Trece la urmatorul filtru din coada
    Sterge filtrul curent si seteaza urmatorul ca fiind activ
    """
    with queue_lock:
        # Sterge filtrul curent din coada daca exista
        if len(queue_data["queue"]) > 0 and queue_data["current_filter"]:
            # Sterge primul element (cel care tocmai s-a terminat)
            queue_data["queue"].popleft()
        
        # Seteaza urmatorul filtru ca fiind activ
        if len(queue_data["queue"]) > 0:
            queue_data["current_filter"] = queue_data["queue"][0]
        else:
            # Daca nu mai sunt filtre, seteaza None
            queue_data["current_filter"] = None
        
        queue_data["total_count"] = len(queue_data["queue"])
    
    # Notifica toate conexiunile SSE
    broadcast_update()


def get_queue_state():
    """
    Obtine starea curenta a cozii pentru afisare
    Returneaza filtrul activ + urmatoarele 3 filtre din coada
    
    Returns:
        dict: Starea cozii cu current_filter, queue (urmatoarele 3) si total_count
    """
    with queue_lock:
        # Sare peste primul element (filtrul curent) si afiseaza urmatoarele 3
        upcoming = list(queue_data["queue"])[1:4] if len(queue_data["queue"]) > 1 else []
        
        # Numarul total exclude filtrul curent (doar cele in asteptare)
        waiting_count = len(queue_data["queue"]) - 1 if len(queue_data["queue"]) > 0 else 0
        
        return {
            "current_filter": queue_data["current_filter"],
            "queue": upcoming,  # Urmatoarele 3 filtre
            "total_count": waiting_count  # Doar cele in asteptare
        }


def broadcast_update():
    """
    Trimite update la toate conexiunile SSE active
    Foloseste format SSE: "data: {...}\\n\\n"
    """
    state = get_queue_state()
    data = f"data: {json.dumps(state)}\\n\\n"
    
    # Trimite la toate conexiunile, sterge cele care au esuat
    for conn in sse_connections[:]:
        try:
            conn.put(data)
        except:
            sse_connections.remove(conn)


@app.route('/')
def index():
    """
    Pagina principala - afiseaza coada de filtre in timp real
    Folosita pentru OBS overlay
    """
    return render_template('queue.html')


@app.route('/menu')
def menu():
    """
    Pagina cu meniul de filtre - afiseaza toate filtrele disponibile cu preturi
    Folosita pentru OBS overlay static
    """
    return render_template('menu.html')


@app.route('/api/queue')
def api_queue():
    """
    API endpoint pentru obtinerea starii cozii ca JSON
    Folosit pentru integrari sau debugging
    """
    return jsonify(get_queue_state())


@app.route('/api/stream')
def stream():
    """
    Endpoint Server-Sent Events pentru update-uri in timp real
    Clientii se conecteaza aici si primesc push notifications automat
    Implementeaza heartbeat la fiecare 30 secunde pentru keep-alive
    """
    import queue
    
    def event_stream():
        # Creeaza o coada separata pentru aceasta conexiune
        q = queue.Queue()
        sse_connections.append(q)
        
        try:
            # Trimite starea initiala la conectare
            state = get_queue_state()
            yield f"data: {json.dumps(state)}\n\n"
            
            # Mentine conexiunea activa si trimite update-uri
            while True:
                try:
                    # Asteapta update (timeout 30 secunde)
                    data = q.get(timeout=30)
                    yield data
                except queue.Empty:
                    # Trimite heartbeat pentru a mentine conexiunea activa
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            # Curata conexiunea cand clientul se deconecteaza
            sse_connections.remove(q)
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/next', methods=['POST'])
def api_next():
    """
    API endpoint pentru avansare manuala la urmatorul filtru
    Folosit pentru testare sau control manual
    """
    next_filter()
    return jsonify({"status": "ok"})


@app.route('/api/add/<filter_name>/<username>/<int:amount>', methods=['POST'])
def api_add(filter_name, username, amount):
    """
    API endpoint pentru adaugare manuala de filtre in coada
    Folosit pentru testare si debugging
    
    Args:
        filter_name: Numele filtrului de adaugat
        username: Numele utilizatorului (simulat)
        amount: Suma de tokeni (simulata)
    """
    add_to_queue(filter_name, username, amount)
    return jsonify({"status": "ok"})


def run_server(host='127.0.0.1', port=8080):
    """
    Porneste serverul Flask
    
    Args:
        host: Adresa IP pe care sa asculte (default: localhost)
        port: Portul pe care sa asculte (default: 8080)
    """
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    print("🎨 Serverul Queue UI porneste pe http://127.0.0.1:8080")
    run_server()
