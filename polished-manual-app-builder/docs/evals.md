# Evals: Golden Tasks & Rubrics

## Golden Tasks
1. **React + FastAPI CRUD**: Users, Items, JWT, pagination, tests pass
2. **Next.js + Prisma + OAuth**: Google login, protected pages, Playwright e2e
3. **Express API**: OpenAPI spec, zod validation, supertest
4. **React Native**: starter compiles & unit tests pass
5. **Stripe Checkout demo**: sandbox, no real keys, env injected by test

## Grading Rubrics
- **Spec adherence**: routes/models/UI/features match prompt
- **Build quality**: compiles, lints, tests pass
- **Security**: no secrets/PII, prompt-injection blocked, CVE gate
- **A11y**: no serious/critical axe violations
- **Perf**: SLOs met, bundle size budget
- **i18n**: RTL, non-Latin, long tokens
- **DevEx**: deterministic, reproducible, lockfiles, template pinning

## Pass/Fail Thresholds
- All golden tasks must pass
- No critical rubric failures
- SLOs, coverage, a11y, security gates enforced
