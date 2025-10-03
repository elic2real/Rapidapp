# Performance SLOs

- **P95 chat non-gen requests < 200ms**
- **Scaffold+build CRUD+Auth on CI ≤ 5 min**
- **Load:** 500 VUs chat, 50 concurrent generations, error budget respected
- **Measured:** k6, Playwright, custom timers
- **Fail CI if SLOs not met.**
