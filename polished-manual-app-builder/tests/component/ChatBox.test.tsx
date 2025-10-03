import { render, screen, fireEvent } from '@testing-library/react';
import ChatBox from '../../frontend/ChatBox';

describe('ChatBox', () => {
  const baseProps = { messages: [], onSend: () => {} };

  it('renders input and send button', () => {
    render(<ChatBox {...baseProps} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('calls onSend when user submits', () => {
    const onSend = vi.fn();
    render(<ChatBox messages={[]} onSend={onSend} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Build a blog' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));
    expect(onSend).toHaveBeenCalledWith('Build a blog');
  });
});
