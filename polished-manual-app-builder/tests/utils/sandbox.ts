export class SandboxFS {
  constructor(private root: string) {}
  readFile(path: string) {
    if (!path.startsWith(this.root)) throw new Error('FS sandbox escape blocked');
    return 'file content';
  }
}
