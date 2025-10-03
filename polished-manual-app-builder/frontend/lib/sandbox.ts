export class SandboxFS {
  private files: Record<string, string> = {};
  private root: string;
  constructor(root: string) {
    this.root = root;
  }
  write(path: string, content: string) {
    this.files[path] = content;
  }
  read(path: string) {
    return this.files[path] || null;
  }
  readFile(path: string) {
    if (!path.startsWith(this.root)) throw new Error('Access denied');
    return this.read(path);
  }
}
