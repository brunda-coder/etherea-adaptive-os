import React from 'react';
import './EthereaAgent.css';

interface EthereaAgentProps {
    mood: string;
    expression: string;
}

const EthereaAgent: React.FC<EthereaAgentProps> = ({ mood, expression }) => {
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
