export class RegistryMock {
  getPackageInfo(name: string) {
    if (name === 'left-pad' || name === 'event-stream') return { deprecated: true, malicious: true };
    return { deprecated: false, malicious: false };
  }
}
