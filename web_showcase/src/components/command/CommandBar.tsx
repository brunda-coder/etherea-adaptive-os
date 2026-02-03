import React, { useState, useEffect } from 'react';

interface CommandBarProps {
    onCommandSubmit: (command: string) => void;
    onOpenChange: (isOpen: boolean) => void;
}

const CommandBar: React.FC<CommandBarProps> = ({ onCommandSubmit, onOpenChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [command, setCommand] = useState('');

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
                event.preventDefault();
                setIsOpen(true);
                onOpenChange(true);
            }
            if (event.key === 'Escape') {
                setIsOpen(false);
                onOpenChange(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onOpenChange]);

    const handleCommandChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCommand(e.target.value);
    };

    const handleCommandSubmit = () => {
        if (command.trim()) {
            onCommandSubmit(command);
        }
        setCommand('');
        setIsOpen(false);
        onOpenChange(false);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-20">
            <div className="glass-panel w-1/2 max-w-2xl rounded-lg p-4">
                <input
                    type="text"
                    value={command}
                    onChange={handleCommandChange}
                    onKeyDown={(e) => e.key === 'Enter' && handleCommandSubmit()}
                    placeholder="What can I help you with?"
                    className="w-full bg-transparent border-none outline-none text-lg placeholder-gray-500"
                    autoFocus
                />
            </div>
        </div>
    );
};

export default CommandBar;
