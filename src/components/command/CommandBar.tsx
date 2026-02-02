import React, { useState, useEffect } from 'react';

const CommandBar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [command, setCommand] = useState('');

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        setIsOpen(true);
      }
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleCommandChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCommand(e.target.value);
  };

  const handleCommandSubmit = () => {
    // Mock command handling
    console.log(`Executing command: ${command}`);
    setCommand('');
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-20">
      <div className="w-1/2 bg-black/30 backdrop-blur-md border border-white/10 rounded-lg shadow-2xl p-4">
        <input
          type="text"
          value={command}
          onChange={handleCommandChange}
          onKeyDown={(e) => e.key === 'Enter' && handleCommandSubmit()}
          placeholder="What can I help you with?"
          className="w-full bg-transparent border-none outline-none text-lg"
        />
      </div>
    </div>
  );
};

export default CommandBar;
