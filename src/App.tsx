import React, { useState } from 'react';
import TopToolbar from './components/layout/TopToolbar';
import LeftWorkspacePanel from './components/workspace/LeftWorkspacePanel';
import EthereaAgent from './components/agent/EthereaAgent';
import CommandBar from './components/command/CommandBar';
import EthereaBrain from './brain';

const App: React.FC = () => {
  const [agentState, setAgentState] = useState(EthereaBrain.interpretCommand(''));
  const [isCommandBarOpen, setIsCommandBarOpen] = useState(false);

  const handleCommandSubmit = (command: string) => {
    setAgentState(EthereaBrain.interpretCommand(command));
    EthereaBrain.sendStateToBackend(); // Placeholder for backend communication
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
        command={EthereaBrain.mood} // Pass mood as command for now
        isCommandBarOpen={isCommandBarOpen}
      />
      <CommandBar 
        onCommandSubmit={handleCommandSubmit} 
        onOpenChange={setIsCommandBarOpen} 
      />
    </div>
  );
};

export default App;
