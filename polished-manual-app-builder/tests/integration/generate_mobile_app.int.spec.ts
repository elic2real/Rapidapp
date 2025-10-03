import { describe, it, expect } from 'vitest';
import { generateApp } from '../../frontend/app-generator';
import { LLMAdapterMock, ToolRunnerMock } from '../mocks';

describe('Integration: Generate Mobile App', () => {
  it('should generate a React Native starter app', async () => {
    const llm = new LLMAdapterMock('react_native');
    const tools = new ToolRunnerMock();
    const repo = await generateApp({ prompt: 'Mobile app with React Native', llm, tools });
    expect(repo.mobile).toMatch(/react native/i);
    expect(repo).toMatchSnapshot();
  });
});
