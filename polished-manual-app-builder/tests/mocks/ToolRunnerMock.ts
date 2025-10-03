export class ToolRunnerMock {
  async run(tool: string, opts: any) {
    return { output: `ran ${tool}` };
  }
}
