import React, { useState, useEffect } from 'react';

const EthereaAgent: React.FC = () => {
  const [message, setMessage] = useState<string | null>(null);

  const showMessage = (msg: string) => {
    setMessage(msg);
    setTimeout(() => {
      setMessage(null);
    }, 3000);
  };

  useEffect(() => {
    // Mock responses
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey) {
        if (event.key === 'k') {
          showMessage('Command palette opened');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <div className="fixed bottom-10 right-10 flex items-center space-x-4">
      {message && (
        <div className="bg-black/30 backdrop-blur-md border border-white/10 rounded-full px-4 py-2 text-sm">
          {message}
        </div>
      )}
      <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full shadow-lg animate-pulse">
      </div>
    </div>
  );
};

export default EthereaAgent;
