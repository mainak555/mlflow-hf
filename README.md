# mlflow-hf

MLflow on Hugging Face Spaces with a pragmatic security pattern:

- Anonymous read-only access for MLflow UI and query APIs.
- Authentication required for write operations (create, update, delete).
- MySQL backend persistence with certificate-based TLS.

This repository demonstrates a practical way to keep experiment visibility open while protecting mutations.

## Why this pattern

MLflow basic auth is typically all-or-nothing. This setup introduces a policy layer at Nginx so you can:

- Keep dashboards discoverable for broad stakeholders.
- Restrict state-changing actions to authenticated users.
- Preserve compatibility with standard MLflow clients.

## Current implementation

Current enforcement is implemented in [app/nginx.conf](app/nginx.conf):

- Auth required for: `/ajax-api/2.0/mlflow/(experiments|runs)/(create|delete|update)`
- Anonymous allowed for all other routes via catch-all proxy.

Current container bootstrap is in [app/Dockerfile](app/Dockerfile):

- Generates `.htpasswd` from `MLFLOW_TRACKING_PASSWORD`.
- Runs [app/mysql_ca.py](app/mysql_ca.py) to materialize MySQL CA cert and append SSL options to `MLFLOW_MYSQL_CONN`.
- Starts MLflow on `127.0.0.1:5000` behind Nginx on `7860`.

## Documentation map

- Architecture and security model: [docs/architecture.md](docs/architecture.md)
- Deployment pipeline and enterprise certificate lifecycle: [docs/deployment.md](docs/deployment.md)

## Quick start

1. Configure repository secrets and variables used by [.github/workflows/pipeline.yml](.github/workflows/pipeline.yml):
	- `HUGGING_FACE_API_KEY`
	- `MLFLOW_TRACKING_PASSWORD`
	- `MLFLOW_TRACKING_USERNAME`
	- `MLFLOW_MYSQL_CONN`
	- `MLFLOW_MYSQL_CA`
	- `HF_REPO` (repository variable)
2. Push changes under `app/` to `master`.
3. GitHub Actions runs [deploy-app.py](deploy-app.py), pushes app artifacts to HF Space, and injects Space secrets.
4. Access the Space URL:
	- Read-only views work anonymously.
	- Write operations prompt for auth.

## Innovation strategy

1. Now: Nginx policy partition for anonymous reads and authenticated writes.
2. Next: Token-based write authorization (header or API token checks at proxy/policy layer).
3. Future: OIDC/Auth-proxy model for enterprise identity, RBAC, and audit trails.

## Known limitations

- Current route protection covers experiments and runs mutations, not every possible MLflow mutation endpoint.
- Basic auth credentials are single-scope and do not provide role granularity.
- CORS is currently permissive in MLflow startup options.

## Troubleshooting

1. Write actions still anonymous:
	- Verify regex and auth block in [app/nginx.conf](app/nginx.conf).
2. MySQL TLS connection errors:
	- Check CA secret formatting and generated `ca.pem` handling in [app/mysql_ca.py](app/mysql_ca.py).
3. Deployment did not update Space:
	- Check [.github/workflows/pipeline.yml](.github/workflows/pipeline.yml) run logs and `HF_REPO` value.
