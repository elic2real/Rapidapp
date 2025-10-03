export function blockNetwork() {
  // Simulate network block for hermetic tests
  globalThis.fetch = () => Promise.reject(new Error('Network blocked'));
}
