# RUNBOOK.md

## Common Tasks
- **Install:** `pnpm install`
- **Test:** `pnpm test` (unit+integration+coverage)
- **E2E:** `pnpm run e2e`
- **Lint/Format:** `pnpm run lint` / `pnpm run format`
- **Typecheck:** `pnpm run typecheck`
- **Perf:** `pnpm run perf`
- **Security:** `pnpm run security`

## Troubleshooting
- Check `.env` and secrets
- Review CI logs and artifacts
- For Playwright: run with `DEBUG=pw:api` for verbose logs
- For k6: check `tests/performance/k6/` for scenarios

## CI/CD
- See `.github/workflows/ci.yml` for pipeline and gates
