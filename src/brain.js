class EthereaBrain {
    constructor() {
        this.mood = 'neutral';
        this.expression = 'idle';
    }

    // Simple command interpreter
    interpretCommand(command) {
        const lowerCmd = command.toLowerCase();
        let newMood = this.mood;
        let newExpression = this.expression;

        if (lowerCmd.includes('focus') || lowerCmd.includes('coding') || lowerCmd.includes('builder')) {
            newMood = 'focus';
        } else if (lowerCmd.includes('deep work') || lowerCmd.includes('flow')) {
            newMood = 'flow';
        } else if (lowerCmd.includes('tired') || lowerCmd.includes('sleep')) {
            newMood = 'tired';
        } else if (lowerCmd.includes('calm') || lowerCmd.includes('rest') || lowerCmd.includes('heal')) {
            newMood = 'soothing';
        } else if (lowerCmd.includes('reset') || lowerCmd.includes('neutral')) {
            newMood = 'neutral';
        }

        if (lowerCmd.length > 0) {
            newExpression = 'thinking';
        } else {
            newExpression = 'idle';
        }

        this.mood = newMood;
        this.expression = newExpression;

        return { mood: this.mood, expression: this.expression };
    }

    // Placeholder for future communication with Python backend
    async sendStateToBackend() {
        const state = {
            mode: this.mood, // Using mood as mode for now
            tone: 'neutral', // Placeholder
            ei: { // Placeholder values
                focus: 0.5,
                stress: 0.2,
                energy: 0.6,
                curiosity: 0.5
            }
        };

        try {
            const response = await fetch('http://localhost:5001/api/update_persona', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(state)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Backend response:', data);
            } else {
                console.error('Backend request failed:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error sending state to backend:', error);
        }
    }
}

export default new EthereaBrain();
