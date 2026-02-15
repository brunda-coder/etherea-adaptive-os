type Message = { role: 'user' | 'etherea' | 'system'; text: string };

export function AgentPanel({ messages }: { messages: Message[] }) {
  return (
    <section className="card">
      <div className="panel-head">
        <h3>Agent</h3>
        <span className="pill">OFFLINE</span>
      </div>
      <div className="chatlog">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
            {message.text}
          </div>
        ))}
      </div>
    </section>
  );
}

export type { Message };
