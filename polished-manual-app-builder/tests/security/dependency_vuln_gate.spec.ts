import { describe, it, expect } from 'vitest';
import { checkRepoQuality } from '../utils/repo_checks';

describe('Security: Dependency Vulnerability Gate', () => {
  it('should fail build on critical CVEs', async () => {
    const result = await checkRepoQuality('/tmp/vuln-repo');
    expect(result.cveCritical).toBe(false);
    expect(result.logs).toMatch(/critical cve/i);
  });
});
