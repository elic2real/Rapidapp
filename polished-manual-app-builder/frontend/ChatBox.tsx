import React from 'react';

type ChatBoxProps = {
  messages: { user: string; text: string }[];
  onSend: (text: string) => void;
};

export default function ChatBox({ messages, onSend }: ChatBoxProps) {
  const [input, setInput] = React.useState('');
  return (
    <div>
      <div>
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.user}:</b> {m.text}
          </div>
        ))}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button
        onClick={() => {
          onSend(input);
          setInput('');
        }}
      >
        Send
      </button>
    </div>
  );
}
