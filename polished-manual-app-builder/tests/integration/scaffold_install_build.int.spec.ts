import { describe, it, expect } from 'vitest';
import { scaffold, installDeps, buildProject } from '../../frontend/app-generator';
import { SandboxFS } from '../utils/sandbox';

describe('Integration: Scaffold, Install, Build', () => {
  it('should scaffold, install, and build a Next.js+Prisma+OAuth app', async () => {
    const fs = new SandboxFS('/tmp/test-nextjs-oauth');
    await scaffold('nextjs+prisma+oauth', fs);
    await installDeps(fs);
    const buildResult = await buildProject(fs);
    expect(buildResult.success).toBe(true);
    expect(buildResult.logs).toMatch(/build completed/i);
  });
});
