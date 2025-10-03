import { describe, it, expect, vi } from 'vitest';
import { ToolRunner } from '../../frontend/app-generator';

describe('ToolRunner', () => {
  it('should sandbox tool execution and return output', async () => {
    const runner = new ToolRunner();
    const output = await runner.run('npm install', { sandbox: true });
    expect(output).toBeDefined();
  });
});
