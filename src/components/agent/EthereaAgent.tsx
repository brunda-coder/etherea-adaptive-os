import React, { useState, useEffect } from 'react';
import './EthereaAgent.css';

interface EthereaAgentProps {
    command: string;
    isCommandBarOpen: boolean;
}

const EthereaAgent: React.FC<EthereaAgentProps> = ({ command, isCommandBarOpen }) => {
    const [mood, setMood] = useState('neutral'); // neutral, focus, tired
    const [expression, setExpression] = useState('idle'); // idle, listening, thinking

    useEffect(() => {
        if (isCommandBarOpen) {
            setExpression('listening');
        } else if (expression === 'listening') {
            // If the command bar was just closed, go into thinking mode briefly
            setExpression('thinking');
            setTimeout(() => setExpression('idle'), 2000); // Revert to idle after 2s
        }
    }, [isCommandBarOpen]);

    useEffect(() => {
        const handleCommand = () => {
            if (!command) return;

            setExpression('thinking');
            setTimeout(() => setExpression('idle'), 2000); // Revert to idle after 2s

            if (command.includes('focus')) {
                setMood('focus');
            } else if (command.includes('tired') || command.includes('sleep')) {
                setMood('tired');
            } else if (command.includes('reset') || command.includes('neutral')) {
                setMood('neutral');
            } 
        };

        handleCommand();
    }, [command]);

    const containerClasses = ['etherea-agent-container', expression].join(' ');
    const auraClasses = ['avatar-aura', mood].join(' ');

    return (
        <div className={containerClasses}>
            <div className={auraClasses}></div>
            <div className="avatar-core">
                <div className="avatar-eyes">
                    <div className="avatar-eye left"></div>
                    <div className="avatar-eye right"></div>
                </div>
            </div>
        </div>
    );
};

export default EthereaAgent;
