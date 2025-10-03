import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'c8',
      reporter: ['text', 'lcov'],
      lines: 90,
      branches: 90,
      functions: 90,
      statements: 90,
      exclude: ['**/tests/fixtures/**', '**/tests/mocks/**'],
    },
    setupFiles: ['./tests/setup.ts'],
    reporters: ['default'],
    maxConcurrency: 8,
    isolate: true,
  },
});
