export class LLMAdapterMock {
  constructor(private scenario: string) {}
  async complete(prompt: string) {
    return this.scenario;
  }
}
