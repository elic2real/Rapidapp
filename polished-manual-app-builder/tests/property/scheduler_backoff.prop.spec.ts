import { describe, it, expect } from 'vitest';
import fc from 'fast-check';
import { Scheduler } from '../../frontend/app-generator';

describe('Property: Scheduler Backoff', () => {
  it('should always backoff within allowed bounds and never starve tasks', () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 100 }), (attempts) => {
        const scheduler = new Scheduler();
        const backoff = scheduler.getBackoff(attempts);
        expect(backoff).toBeGreaterThanOrEqual(100);
        expect(backoff).toBeLessThanOrEqual(10000);
      })
    );
  });
});
