import React, { useState, useEffect, useCallback } from 'react';
import TopToolbar from './components/layout/TopToolbar';
import LeftWorkspacePanel from './components/workspace/LeftWorkspacePanel';
import EthereaAgent from './components/agent/EthereaAgent';
import CommandBar from './components/command/CommandBar';

// --- Local AI Brain & State ---
type AgentExpression = "neutral" | "attentive" | "focused" | "gentle_concern" | "reassurance";
interface AgentState {
  expression: AgentExpression;
  response: string | null;
}

const App: React.FC = () => {
  const [isFocusMode, setFocusMode] = useState(false);
  const [agentState, setAgentState] = useState<AgentState>({ expression: 'neutral', response: null });
  const [isCommandBarOpen, setIsCommandBarOpen] = useState(false);
  const [auraVisible, setAuraVisible] = useState(false);

  // --- LOCAL "AI" BRAIN ---
  const handleCommand = useCallback((command: string) => {
    const cleanedCommand = command.toLowerCase().trim();
    let nextExpression: AgentExpression = 'reassurance';
    let nextResponse: string | null = null;
    
    switch (cleanedCommand) {
      case "start focus":
      case "help me focus":
        setFocusMode(true);
        nextExpression = 'focused';
        nextResponse = "Entering focus mode. I'll be here to help you concentrate.";
        break;
      case "stop focus":
        setFocusMode(false);
        nextExpression = 'neutral';
        nextResponse = "Focus session complete. Well done.";
        break;
      case "i'm tired":
      case "i am tired":
        nextExpression = 'gentle_concern';
        nextResponse = "It's important to rest. Perhaps a short break would help?";
        break;
      case "open workspace":
         nextResponse = "The workspace is already open, I am here to help you.";
         break;
      default:
        nextExpression = 'neutral';
        nextResponse = "I'm not sure how to respond to that, but I'm here to help.";
        break;
    }
    
    setAgentState({ expression: nextExpression, response: nextResponse });
    // Response fades out after a few seconds
    setTimeout(() => setAgentState(prevState => ({ ...prevState, response: null })), 5000);
  }, []);

  // --- Effects ---
  useEffect(() => {
    // Show aura after initial load
    const timer = setTimeout(() => setAuraVisible(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    document.body.classList.toggle('focus-mode', isFocusMode);
  }, [isFocusMode]);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (isCommandBarOpen) {
      setAgentState(prevState => ({ ...prevState, expression: 'attentive' }));
    } else {
      // Delay returning to neutral in case a command was just submitted
      timeoutId = setTimeout(() => {
        setAgentState(prevState => ({ ...prevState, expression: isFocusMode ? 'focused' : 'neutral' }));
      }, 500);
    }
    return () => clearTimeout(timeoutId);
  }, [isCommandBarOpen, isFocusMode]);
  
  return (
    <div className="w-full h-screen overflow-hidden">
      <div className={`aura-container ${auraVisible ? 'visible' : ''}`}>
        <div className="aura"></div>
      </div>
      
      <TopToolbar />
      <LeftWorkspacePanel />

      <main className="main-canvas">
        <div className="glass-panel w-full h-full rounded-2xl p-8 flex flex-col items-center justify-center text-center">
          {agentState.response && (
            <div className="absolute top-8 text-lg text-blue-300 transition-opacity duration-500">
              {agentState.response}
            </div>
          )}
          
          <h1 className="text-5xl font-bold mb-4 text-gray-100">
            {isFocusMode ? "Focus Session Active" : "Welcome to Etherea"}
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl">
            {isFocusMode 
              ? "The world is quiet. Your mind is clear. Breathe and begin."
              : "Your AI-powered workspace for deep focus and mindful productivity."}
          </p>
          <p className="text-md text-gray-400 mt-6">
            Press <kbd className="px-2 py-1.5 text-xs font-semibold text-gray-300 bg-gray-800 border border-gray-700 rounded-lg">Ctrl+K</kbd> to begin.
          </p>
        </div>
      </main>

      <EthereaAgent expression={agentState.expression} />
      
      <CommandBar 
        onCommandSubmit={handleCommand}
        onOpenChange={setIsCommandBarOpen}
      />
    </div>
  );
};

export default App;
