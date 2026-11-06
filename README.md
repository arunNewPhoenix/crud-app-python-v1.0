# Order Management API — GitHub Integration

A small, production-oriented learning repository for **DevOps Project 01**. It provides a FastAPI order service backed by PostgreSQL, uses Redis to cache `GET /orders`, exposes health and Prometheus metrics endpoints, and validates changes through GitHub Actions.

## Technology

- Python 3.12, FastAPI, Pydantic
- PostgreSQL 16, SQLAlchemy 2
- Redis 7
- Pytest, HTTPX, Fakeredis
- GitHub Actions, Ruff, CodeQL, Dependency Review, Gitleaks

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/orders` | List orders; Redis cache with PostgreSQL fallback |
| POST | `/orders` | Create an order and invalidate the list cache |
| GET | `/health` | Check PostgreSQL and Redis connectivity |
| GET | `/metrics` | Prometheus metrics (excluded from OpenAPI schema) |
| GET | `/docs` | Interactive Swagger documentation |

Example request:

```bash
curl -X POST http://localhost:8000/orders \\
  -H 'Content-Type: application/json' \\
  -d '{"customer_name":"Asha","item":"Keyboard","quantity":2,"unit_price":1499}'
```

## Run locally

Prerequisites: Python 3.12+, Docker and Docker Compose.

```bash
cp .env.example .env
docker compose up -d
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

## Run checks

```bash
ruff check .
pytest -q
```

Tests use an isolated in-memory SQLite database and fake Redis. They do not require running PostgreSQL or Redis. The local `/health` endpoint checks the real services configured in `.env`.

## Git workflow

Use short-lived branches and pull requests. Suggested branch names:

- `feat/add-order-status`
- `fix/cache-invalidation`
- `docs/improve-setup-guide`
- `test/add-order-validation`

Commit format (Conventional Commits):

```text
<type>(<scope>): <imperative summary>

feat(orders): add order creation endpoint
fix(cache): invalidate order list after creation
test(api): cover invalid order quantity
```

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, `revert`.

## GitHub repository settings checklist

After pushing this repository to GitHub:

1. Set `main` as the default branch.
2. Under **Settings → Rules → Rulesets** (or Branches → branch protection), create a rule targeting `main`.
3. Require a pull request before merging and require at least **1 approval**.
4. Dismiss stale approvals when new commits are pushed; require conversation resolution.
5. Require the `Lint and test` status check before merging. Push a first PR so GitHub discovers the check name.
6. Block force pushes and branch deletion. Do not allow bypass for routine contributors.
7. Enable **Secret scanning** and **Push protection** where available for the repository/plan.
8. Enable **Dependabot alerts** and **Dependabot security updates** under Security settings.
9. Keep Actions permissions read-only by default; workflows declare only the permissions they need.

Branch protection, required reviews, repository secret scanning and Dependabot settings are GitHub-hosted settings; files in Git cannot switch them on automatically. The workflow includes Gitleaks, CodeQL and PR dependency review as repository-level checks.

## Security notes

- Never commit `.env`, tokens, passwords, private keys or production data.
- Use GitHub Actions secrets / OIDC for later cloud deployment; do not hardcode credentials in workflow files.
- Pin third-party Actions to full commit SHAs before treating this as a hardened production pipeline. Major-version tags are used here for readability in a learning repo.
- This sample uses `create_all()` for quick local setup. Replace it with Alembic migrations before evolving a production schema.
- Add authentication, authorization, pagination, idempotency, structured JSON logs, tracing, rate limits and API contract tests before exposing the service publicly.

## Suggested project acceptance criteria

- [ ] Repository is public or shared with the intended reviewer.
- [ ] README setup works on a clean machine.
- [ ] `ruff check .` passes.
- [ ] `pytest -q` passes in GitHub Actions.
- [ ] PR template appears on new pull requests.
- [ ] A feature branch is merged through a reviewed PR.
- [ ] `main` rejects direct pushes and unreviewed changes.
- [ ] Secret and dependency scanning are enabled and verified.
- [ ] No credentials are present in Git history.

## License

MIT. See [LICENSE](LICENSE).
