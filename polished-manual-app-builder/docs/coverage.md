# Coverage Policy

- **Target:** ≥90% lines/branches/functions for core libs/services, ≥80% for UI, all measured in CI.
- **Tools:** Vitest (c8), Playwright, Pytest (Python), k6 (perf).
- **Exclusions:** test/mocks/fixtures, generated code, config files.
- **Fail CI if below threshold.**
