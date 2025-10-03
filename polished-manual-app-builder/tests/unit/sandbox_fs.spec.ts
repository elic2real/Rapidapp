import { describe, it, expect } from 'vitest';
import { SandboxFS } from '../../frontend/lib/sandbox';

describe('SandboxFS', () => {
  it('should block access outside project root', () => {
    const fs = new SandboxFS('/tmp/project');
    expect(() => fs.readFile('/etc/passwd')).toThrow();
  });
});
