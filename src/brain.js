const EthereaBrain = {
  // Initial State
  state: {
    mood: 'neutral', // neutral, focus, tired, flow, soothing
    expression: 'idle', // idle, listening, thinking, speaking
    lastMode: 'neutral',
    sessionStartTime: null,
    recentCommands: [],
  },

  // Rules and Heuristics
  rules: {
    greetings: ['hello', 'hi', 'hey'],
    focus: ['focus', 'work', 'start'],
    tired: ['tired', 'sleepy', 'exhausted'],
    help: ['help', 'assist'],
    memory: ['remember', 'log', 'note'],
  },

  // Command Interpretation
  interpretCommand(command) {
    const lowerCmd = command.toLowerCase();
    let newState = { ...this.state, expression: 'thinking' };

    if (this.rules.greetings.some(word => lowerCmd.includes(word))) {
      newState.mood = 'neutral';
    } else if (this.rules.focus.some(word => lowerCmd.includes(word))) {
      newState.mood = 'focus';
    } else if (this.rules.tired.some(word => lowerCmd.includes(word))) {
      newState.mood = 'tired';
    } else if (this.rules.help.some(word => lowerCmd.includes(word))) {
      newState.mood = 'soothing';
    } else if (this.rules.memory.some(word => lowerCmd.includes(word))) {
      newState.mood = 'flow';
    } else {
      newState.expression = 'idle'; // Command not understood
    }

    this.state = newState;
    this.state.recentCommands.push(command);
    return this.state;
  },

  // Session Management (placeholder for now)
  startSession() {
    this.state.sessionStartTime = new Date();
  },

  endSession() {
    this.state.sessionStartTime = null;
  },
  
  // Send state to a backend or local storage
  sendStateToBackend() {
    // In a real scenario, this would send state to a backend or save to localStorage
    console.log("New State:", this.state);
  }
};

export default EthereaBrain;
