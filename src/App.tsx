import React from 'react';
import TopToolbar from './layout/TopToolbar';
import LeftWorkspacePanel from './workspace/LeftWorkspacePanel';
import EthereaAgent from './agent/EthereaAgent';
import CommandBar from './command/CommandBar';

const App: React.FC = () => {
  return (
    <div className="w-full h-screen bg-gradient-to-br from-[#1a1b26] to-[#2a2c3d] text-[#a9b1d6]">
      <TopToolbar />
      <LeftWorkspacePanel />
      <div className="ml-72 h-full p-8">
        <div className="w-full h-full bg-black/10 rounded-2xl">
          {/* Main Canvas Content Here */}
        </div>
      </div>
      <EthereaAgent />
      <CommandBar />
    </div>
  );
};

export default App;
