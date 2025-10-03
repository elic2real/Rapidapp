import { render, screen } from '@testing-library/react';
import BuildStatusBadge from '../../frontend/BuildStatusBadge';

describe('BuildStatusBadge', () => {
  it('shows success badge', () => {
    render(<BuildStatusBadge status="success" />);
    expect(screen.getByLabelText(/build succeeded/i)).toBeInTheDocument();
  });
  it('shows error badge', () => {
    render(<BuildStatusBadge status="error" />);
    expect(screen.getByLabelText(/build failed/i)).toBeInTheDocument();
  });
});
