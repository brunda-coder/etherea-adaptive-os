from flask import Flask, send_from_directory, request, jsonify
import datetime
import random

# Initialize the Flask Bridge
app = Flask(__name__, static_url_path='')

# --- MOCKING YOUR CORE MODULES FOR MOBILE ---
# (Since we can't load the full Desktop GUI on phone, we link to the logic)
def get_ei_status():
    # Linking to "EI Signals (Chinmai)" 
    return {
        "focus": random.randint(70, 95), # Mock sensor data
        "stress": random.randint(10, 30),
        "status": "Optimal"
    }

def get_logs():
    # Linking to "Workspace Data (Chandramma)" 
    return [
        "User: Brunda G verified",
        "System: Professional Mode Active",
        "Network: Secure (Offline-First)"
    ]

# --- THE SERVER ROUTES ---

@app.route('/')
def home():
    # Serves your "Face" (index.html)
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    # This is the "Professional Chat Mode" [cite: 8]
    user_input = request.json.get('message', '').lower()
    
    # LOGIC PROCESSING
    if "status" in user_input:
        data = get_ei_status()
        response = f"Focus: {data['focus']}% | Stress: {data['stress']}% | System: {data['status']}"
    elif "logs" in user_input:
        logs = get_logs()
        response = "Latest Logs:\n" + "\n".join(logs)
    elif "hello" in user_input:
        response = "Hello, Bru. I am ready for task execution."
    else:
        response = f"Processing command: '{user_input}'. (Simulating Core Execution)"
    
    return jsonify({"response": response})

@app.route('/api/metrics', methods=['GET'])
def metrics():
    # Feeds the Dashboard [cite: 9]
    return jsonify(get_ei_status())

if __name__ == '__main__':
    print("🚀 Etherea Smart Server Online on Port 8080")
    app.run(host='0.0.0.0', port=8080)
