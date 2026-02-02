import React, { useState, useEffect } from 'react';
import TopToolbar from './components/layout/TopToolbar';
import LeftWorkspacePanel from './components/workspace/LeftWorkspacePanel';
import EthereaAgent from './components/agent/EthereaAgent';
import CommandBar from './components/command/CommandBar';
import EthereaBrain from './brain';
import './aura.css';

const App: React.FC = () => {
  const [agentState, setAgentState] = useState({ mood: 'neutral', expression: 'idle' });
  const [isCommandBarOpen, setIsCommandBarOpen] = useState(false);

  useEffect(() => {
    if (isCommandBarOpen) {
      setAgentState(prevState => ({ ...prevState, expression: 'listening' }));
    } else {
      // Only revert to idle if the agent was listening (i.e., command bar was closed without submitting)
      setAgentState(prevState => {
        if (prevState.expression === 'listening') {
          return { ...prevState, expression: 'idle' };
        }
        return prevState;
      });
    }
  }, [isCommandBarOpen]);

  const handleCommandSubmit = (command: string) => {
    const newState = EthereaBrain.interpretCommand(command);
    setAgentState(newState); // This will set expression to 'thinking'
    EthereaBrain.sendStateToBackend();

    // After thinking, revert to idle
    setTimeout(() => {
      setAgentState(prevState => ({ ...prevState, expression: 'idle' }));
    }, 2000);
  };

  const auraClasses = ['aura', `aura-${agentState.mood}`].join(' ');

  return (
    <div className="w-full h-screen text-[#a9b1d6]">
      <div className={auraClasses}></div>
      <TopToolbar />
      <LeftWorkspacePanel />
      <main className="main-canvas">
        <div className="text-center p-8">
          <h1 className="text-4xl font-bold mb-4">Welcome to Etherea</h1>
          <p className="text-lg">Your AI-powered workspace for focus and productivity.</p>
          <p className="text-lg mt-2">Press <kbd>Ctrl+K</kbd> or <kbd>Cmd+K</kbd> to get started.</p>
        </div>
      </main>
      <EthereaAgent 
        mood={agentState.mood}
        expression={agentState.expression}
      />
      <CommandBar 
        onCommandSubmit={handleCommandSubmit} 
        onOpenChange={setIsCommandBarOpen} 
      />
    </div>
  );
};

export default App;
