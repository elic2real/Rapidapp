export class ChatController {
  constructor(llm: Record<string, unknown>, tools: Record<string, unknown>);
  plan(prompt: string): Promise<string>;
  runTool(tool: string, opts: Record<string, unknown>): Promise<unknown>;
}
