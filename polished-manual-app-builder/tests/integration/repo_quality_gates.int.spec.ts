import { describe, it, expect } from 'vitest';
import { checkRepoQuality } from '../utils/repo_checks';

describe('Integration: Repo Quality Gates', () => {
  it('should enforce lint, test, and license gates on generated repo', async () => {
    const result = await checkRepoQuality('/tmp/generated-repo');
    expect(result.lint).toBe(true);
    expect(result.tests).toBe(true);
    expect(result.license).toBe(true);
    expect(result.bundleSize).toBeLessThan(5 * 1024 * 1024); // 5MB
  });
});
