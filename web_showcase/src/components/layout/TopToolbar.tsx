import React from 'react';
import { HomeIcon, FocusIcon, WorkspaceIcon, JournalIcon, SettingsIcon } from '../icons';

const TopToolbar: React.FC = () => {
  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50">
      <div className="glass-panel flex items-center space-x-2 rounded-full p-2">
        <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
          <HomeIcon />
        </button>
        <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
          <FocusIcon />
        </button>
        <button className="p-2 rounded-full bg-white/10 transition-colors">
          <WorkspaceIcon />
        </button>
        <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
          <JournalIcon />
        </button>
        <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
          <SettingsIcon />
        </button>
      </div>
    </div>
  );
};

export default TopToolbar;
