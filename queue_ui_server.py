"""
Queue UI Server - Displays the filter queue in real-time for OBS integration
"""
from flask import Flask, render_template, jsonify, Response
import json
import time
import threading
from collections import deque

app = Flask(__name__)

# Global queue data
queue_data = {
    "current_filter": None,
    "queue": deque(maxlen=50),  # Maximum 50 items in queue
    "total_count": 0
}

# Thread lock for queue data
queue_lock = threading.Lock()

# SSE connections
sse_connections = []


def add_to_queue(filter_name, username, amount):
    """Add a filter to the queue"""
    with queue_lock:
        queue_data["queue"].append({
            "filter": filter_name,
            "username": username,
            "amount": amount,
            "timestamp": time.time()
        })
        
        # If no current filter, set the first one as current but DON'T remove from queue yet
        if queue_data["current_filter"] is None and len(queue_data["queue"]) > 0:
            queue_data["current_filter"] = queue_data["queue"][0]
        
        queue_data["total_count"] = len(queue_data["queue"])
    
    # Notify all SSE connections
    broadcast_update()


def next_filter():
    """Move to the next filter in queue"""
    with queue_lock:
        # Remove the current filter from queue if it exists
        if len(queue_data["queue"]) > 0 and queue_data["current_filter"]:
            # Remove first item (the one that was just playing)
            queue_data["queue"].popleft()
        
        # Set next filter as current
        if len(queue_data["queue"]) > 0:
            queue_data["current_filter"] = queue_data["queue"][0]
        else:
            queue_data["current_filter"] = None
        
        queue_data["total_count"] = len(queue_data["queue"])
    
    broadcast_update()


def get_queue_state():
    """Get current queue state"""
    with queue_lock:
        # Skip first item (current filter) and show next 3
        upcoming = list(queue_data["queue"])[1:4] if len(queue_data["queue"]) > 1 else []
        # Total count should exclude the current filter
        waiting_count = len(queue_data["queue"]) - 1 if len(queue_data["queue"]) > 0 else 0
        return {
            "current_filter": queue_data["current_filter"],
            "queue": upcoming,  # Show next 3 after current
            "total_count": waiting_count  # Only count items waiting, not current
        }


def broadcast_update():
    """Broadcast queue update to all SSE connections"""
    state = get_queue_state()
    data = f"data: {json.dumps(state)}\n\n"
    
    for conn in sse_connections[:]:
        try:
            conn.put(data)
        except:
            sse_connections.remove(conn)


@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('queue.html')


@app.route('/menu')
def menu():
    """Serve the menu page"""
    return render_template('menu.html')


@app.route('/api/queue')
def api_queue():
    """Get current queue state as JSON"""
    return jsonify(get_queue_state())


@app.route('/api/stream')
def stream():
    """Server-Sent Events endpoint for real-time updates"""
    import queue
    
    def event_stream():
        q = queue.Queue()
        sse_connections.append(q)
        
        try:
            # Send initial state
            state = get_queue_state()
            yield f"data: {json.dumps(state)}\n\n"
            
            # Keep connection alive and send updates
            while True:
                try:
                    data = q.get(timeout=30)  # 30 second timeout
                    yield data
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            sse_connections.remove(q)
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/next', methods=['POST'])
def api_next():
    """Manually trigger next filter"""
    next_filter()
    return jsonify({"status": "ok"})


@app.route('/api/add/<filter_name>/<username>/<int:amount>', methods=['POST'])
def api_add(filter_name, username, amount):
    """Manually add filter to queue (for testing)"""
    add_to_queue(filter_name, username, amount)
    return jsonify({"status": "ok"})


def run_server(host='127.0.0.1', port=8080):
    """Run the Flask server"""
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    print("🎨 Queue UI Server starting on http://127.0.0.1:8080")
    run_server()
