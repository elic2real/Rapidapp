export function generateApp(spec: Record<string, unknown>): unknown;
export function scaffold(...args: unknown[]): unknown;
export function installDeps(...args: unknown[]): unknown;
export function buildProject(...args: unknown[]): unknown;

export class PlannerOrchestrator {
  plan(prompt: string): Record<string, unknown>;
}

export class Scheduler {
  getBackoff(attempts: number): number;
}

export class ToolRunner {
  run(tool: string, opts: Record<string, unknown>): Promise<unknown>;
}
