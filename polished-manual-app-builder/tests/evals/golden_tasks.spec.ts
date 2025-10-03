import { describe, it, expect } from 'vitest';
import { generateApp } from '../../frontend/app-generator';

describe('Evals: Golden Tasks', () => {
  it('should pass React+FastAPI CRUD golden task', async () => {
    const repo = await generateApp({ prompt: 'CRUD app with React and FastAPI' });
    expect(repo).toMatchObject({ frontend: expect.any(String), backend: expect.any(String) });
    expect(repo).toMatchSnapshot();
  });
  // ...repeat for other golden tasks
});
