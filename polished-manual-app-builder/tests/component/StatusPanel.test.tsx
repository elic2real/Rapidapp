import { render, screen } from '@testing-library/react';
import StatusPanel from '../../frontend/StatusPanel';

describe('StatusPanel', () => {
  it('shows build status and progress', () => {
    render(<StatusPanel status="building" progress={42} />);
    expect(screen.getByText(/building/i)).toBeInTheDocument();
    expect(screen.getByText(/42%/)).toBeInTheDocument();
  });
});
