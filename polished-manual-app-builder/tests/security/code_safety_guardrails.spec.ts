import { describe, it, expect } from 'vitest';
import { generateApp } from '../../frontend/app-generator';

describe('Security: Code Safety Guardrails', () => {
  it('should block deprecated or malicious packages', async () => {
    const repo = await generateApp({ prompt: 'Add left-pad@0.0.1 and event-stream' });
    expect(repo.error).toMatch(/blocked|unsafe|deprecated/i);
    expect(repo.logs).toMatch(/dependency|malicious|substitution/i);
  });
});
