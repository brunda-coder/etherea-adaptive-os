import React from 'react';
import './EthereaAgent.css';

type AgentExpression = "neutral" | "attentive" | "focused" | "gentle_concern" | "reassurance";

interface EthereaAgentProps {
    expression: AgentExpression;
}

const EthereaAgent: React.FC<EthereaAgentProps> = ({ expression }) => {
    const containerClasses = ['etherea-agent-container', `expression-${expression}`].join(' ');

    return (
        <div className={containerClasses}>
            <div className="agent-body">
                <div className="agent-glow"></div>
                <div className="agent-core"></div>
                <div className="agent-eyes">
                    <div className="agent-eye left"></div>
                    <div className="agent-eye right"></div>
                </div>
            </div>
        </div>
    );
};

export default EthereaAgent;
