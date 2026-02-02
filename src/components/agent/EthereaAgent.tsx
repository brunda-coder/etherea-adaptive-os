import React, { useState, useEffect } from 'react';
import './EthereaAgent.css';

interface EthereaAgentProps {
    command: string;
    isCommandBarOpen: boolean;
}

const EthereaAgent: React.FC<EthereaAgentProps> = ({ command, isCommandBarOpen }) => {
    const [mood, setMood] = useState('neutral'); // neutral, focus, tired, flow, soothing
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
            setTimeout(() => setExpression('idle'), 2000);

            if (command.includes('focus') || command.includes('coding') || command.includes('builder')) {
                setMood('focus');
            } else if (command.includes('deep work') || command.includes('flow')) {
                setMood('flow');
            } else if (command.includes('tired') || command.includes('sleep')) {
                setMood('tired');
            } else if (command.includes('calm') || command.includes('rest') || command.includes('heal')) {
                setMood('soothing');
            } else if (command.includes('reset') || command.includes('neutral')) {
                setMood('neutral');
            }
        };

        handleCommand();
    }, [command]);

    // Apply mood and expression to the container for cascading styles
    const containerClasses = ['etherea-agent-container', expression, mood].join(' ');

    return (
        <div className={containerClasses}>
            <div className="avatar-aura"></div>
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
