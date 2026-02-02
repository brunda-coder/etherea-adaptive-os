import React, { useState, useEffect } from 'react';
import TopToolbar from './components/layout/TopToolbar';
import LeftWorkspacePanel from './components/workspace/LeftWorkspacePanel';
import EthereaAgent from './components/agent/EthereaAgent';
import CommandBar from './components/command/CommandBar';
import EthereaBrain from './brain';

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

  return (
    <div className="w-full h-screen bg-gradient-to-br from-[#1a1b26] to-[#2a2c3d] text-[#a9b1d6]">
      <TopToolbar />
      <LeftWorkspacePanel />
      <div className="ml-72 h-full p-8">
        <div className="w-full h-full bg-black/10 rounded-2xl">
          {/* Main Canvas Content Here */}
        </div>
      </div>
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
