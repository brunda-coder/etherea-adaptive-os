from flask import Flask, request, jsonify
from corund.avatar.persona_engine import PersonaEngine

app = Flask(__name__)
persona_engine = PersonaEngine()

@app.route('/api/update_persona', methods=['POST'])
def update_persona():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract data for the persona engine
    mode = data.get('mode', 'study')
    tone = data.get('tone', 'neutral')
    ei = data.get('ei', {})

    # Compute the new persona state
    persona_state = persona_engine.compute(mode=mode, tone=tone, ei=ei)

    # In a real application, you would do something with this state,
    # like sending it to the avatar, logging it, etc.
    print(f"New persona state: {persona_state}")

    return jsonify(persona_state)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
