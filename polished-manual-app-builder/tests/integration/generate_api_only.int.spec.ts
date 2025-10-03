import { describe, it, expect } from 'vitest';
import { generateApp } from '../../frontend/app-generator';
import { LLMAdapterMock, ToolRunnerMock } from '../mocks';

describe('Integration: Generate API-Only App', () => {
  it('should generate an Express API-only app', async () => {
    const llm = new LLMAdapterMock('express_api');
    const tools = new ToolRunnerMock();
    const repo = await generateApp({ prompt: 'API-only app with Express', llm, tools });
    expect(repo.backend).toMatch(/express/i);
    expect(repo.frontend).toBeUndefined();
    expect(repo).toMatchSnapshot();
  });
});
