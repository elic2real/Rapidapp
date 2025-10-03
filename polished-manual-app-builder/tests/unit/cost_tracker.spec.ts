import { describe, it, expect } from 'vitest';
import { CostTracker } from '../../frontend/lib/cost-tracker';

describe('CostTracker', () => {
  it('should track and cap LLM/tool costs', () => {
    const tracker = new CostTracker(100);
    tracker.add(10);
    tracker.add(20);
    expect(tracker.total()).toBe(30);
    expect(() => tracker.add(100)).toThrow();
  });
});
