# Test Plan: App-Making App

## Scope
- Node/TypeScript frontend (React/Next.js) + orchestrator service
- Alt backends (Python/Go/Rails) via adapters/mocks
- Chat UI: user requests app, system plans, scaffolds, installs, builds, validates, returns repo

## Risks
- LLM hallucination/spec drift
- Prompt injection, data leakage, dependency vulns
- Accessibility, performance, concurrency, i18n
- Determinism, reproducibility, sandbox escape

## Test Matrix
| Area         | Unit | Component | Integration | E2E | Security | Perf | A11y | Property | Evals |
|--------------|------|-----------|-------------|-----|----------|------|------|----------|-------|
| Chat/Plan    |  X   |     X     |      X      |  X  |    X     |      |      |    X     |   X   |
| Scaffold/FS  |  X   |     X     |      X      |  X  |    X     |      |      |    X     |   X   |
| Build/CI     |  X   |     X     |      X      |  X  |    X     |  X   |      |    X     |   X   |
| A11y         |      |     X     |      X      |  X  |          |      |  X   |          |       |
| Security     |      |           |      X      |  X  |    X     |      |      |          |   X   |
| i18n         |      |     X     |      X      |  X  |          |      |      |          |       |
| Perf/SLO     |      |           |      X      |  X  |          |  X   |      |          |       |
| Privacy      |      |           |      X      |  X  |    X     |      |      |          |       |

## Exit Criteria
- All test stages green
- Coverage ≥ 90% (lines/branches/functions)
- Zero serious a11y issues
- No critical CVEs
- SLOs met
- Generated apps compile/lint/test
- No secrets/PII in logs
- Golden tasks pass

## Coverage Targets
- ≥90% line/branch/function (enforced in CI)

## SLOs
- P95 chat non-gen requests < 200ms
- Scaffold+build CRUD+Auth on CI ≤ 5 min
- Load: 500 VUs chat, 50 concurrent generations, error budget respected

## Data Policy
- No secrets/PII in logs/artifacts
- .env handling, retention, license checks

## How to Run
- `pnpm test` (all)
- `pnpm test:unit`, `pnpm test:int`, `pnpm test:e2e`, `pnpm test:security`, `pnpm test:perf`
- See `.github/workflows/ci.yml` for full matrix
