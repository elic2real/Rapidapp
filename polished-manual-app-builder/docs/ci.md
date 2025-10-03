# CI/CD Pipeline

- **Stages:** lint → typecheck → unit → integration → e2e → security → perf
- **Matrix:** Node LTS/current, Playwright browsers
- **Caching:** pnpm/npm, pip, Playwright, k6
- **Artifacts:** coverage, Playwright traces, k6 perf, logs
- **Gates:** fail on coverage, a11y, security, perf, SLOs
- **See:** `.github/workflows/ci.yml`
