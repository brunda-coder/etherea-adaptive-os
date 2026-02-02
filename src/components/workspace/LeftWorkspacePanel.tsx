import React from 'react';

const LeftWorkspacePanel: React.FC = () => {
  return (
    <div className="fixed top-0 left-0 h-full w-72 bg-black/10 backdrop-blur-md border-r border-white/10 p-6">
      <h2 className="text-xl font-bold mb-6">Etherea</h2>
      <div>
        <h3 className="text-lg font-semibold mb-4">Tasks</h3>
        <ul>
          <li className="flex items-center mb-2">
            <input type="checkbox" className="mr-2" />
            <span>Finalize Q3 report</span>
          </li>
          <li className="flex items-center mb-2">
            <input type="checkbox" className="mr-2" checked />
            <span>Review design mockups</span>
          </li>
          <li className="flex items-center mb-2">
            <input type="checkbox" className="mr-2" />
            <span>Prepare for team sync</span>
          </li>
        </ul>
      </div>
      <div className="absolute bottom-6 left-6 right-6">
        <h3 className="text-lg font-semibold mb-4">Focus Session</h3>
        <div className="text-4xl font-bold text-center">25:00</div>
      </div>
    </div>
  );
};

export default LeftWorkspacePanel;
