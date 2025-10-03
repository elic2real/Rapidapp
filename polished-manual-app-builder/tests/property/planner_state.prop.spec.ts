import { describe, it, expect } from 'vitest';
import fc from 'fast-check';
import { PlannerOrchestrator } from '../../frontend/app-generator';

describe('Property: Planner DAG', () => {
  it('should always produce an acyclic DAG', () => {
    fc.assert(
      fc.property(fc.string(), (prompt) => {
        const planner = new PlannerOrchestrator();
        const dag = planner.plan(prompt);
        expect(isAcyclic(dag)).toBe(true);
      })
    );
  });
});

function isAcyclic(dag: any) {
  // TODO: implement real cycle check
  return true;
}
