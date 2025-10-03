import { describe, it, expect } from 'vitest';
import { generateApp } from '../../frontend/app-generator';

describe('Evals: Hallucination & Spec Adherence', () => {
  it('should not hallucinate features not in prompt', async () => {
    const repo = await generateApp({ prompt: 'API-only app' });
    expect(repo.frontend).toBeUndefined();
    expect(repo.backend).toMatch(/api/i);
  });
});
