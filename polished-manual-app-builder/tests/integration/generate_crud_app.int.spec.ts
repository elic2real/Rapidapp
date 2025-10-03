import { describe, it, expect } from 'vitest';
import { generateApp } from '../../frontend/app-generator';
import { LLMAdapterMock, ToolRunnerMock } from '../mocks';

describe('Integration: Generate CRUD App', () => {
  it('should generate a React+FastAPI CRUD app deterministically', async () => {
    const llm = new LLMAdapterMock('react+fastapi_crud');
    const tools = new ToolRunnerMock();
    const repo = await generateApp({ prompt: 'CRUD app with React and FastAPI', llm, tools });
    expect(repo).toMatchObject({
      frontend: expect.any(String),
      backend: expect.any(String),
      tests: expect.any(Array)
    });
    // Golden repo snapshot check
    expect(repo).toMatchSnapshot();
  });
});
