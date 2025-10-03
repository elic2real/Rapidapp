import { describe, it, expect, vi } from 'vitest';
import { ChatController } from '../../frontend/ai-orchestrator';

describe('ChatController', () => {
  it('should plan and route user prompts deterministically', async () => {
    // Mock LLM and tool runner
    const llm = { complete: vi.fn().mockResolvedValue('plan') };
    const tools = { run: vi.fn().mockResolvedValue('result') };
    const chat = new ChatController(llm, tools);
    const plan = await chat.plan('Build a todo app');
    expect(plan).toBe('plan');
    const result = await chat.runTool('scaffold', {});
    expect(result).toBe('result');
  });

  it('should be idempotent for same prompt', async () => {
    const llm = { complete: vi.fn().mockResolvedValue('plan') };
    const chat = new ChatController(llm, {});
    const plan1 = await chat.plan('CRUD app');
    const plan2 = await chat.plan('CRUD app');
    expect(plan1).toBe(plan2);
  });
});
