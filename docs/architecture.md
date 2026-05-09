# Architecture: Secure MLflow With Anonymous Read-Only

## Goal

Provide a secure MLflow deployment where:

- Anonymous users can view experiments and runs.
- Authenticated users can create, update, and delete tracking data.
- Backend state is persisted in MySQL over certificate-based TLS.

## Current architecture

```mermaid
flowchart LR
    A[Anonymous or Admin User] --> B[Hugging Face Space Endpoint]
    B --> C[Nginx Policy Layer :7860]
    C -->|Allowed read routes| D[MLflow Server :5000 localhost]
    C -->|Write routes require Basic Auth| D
    D -->|SQLAlchemy + PyMySQL over TLS| E[(MySQL Backend)]

    F[GitHub Actions] --> G[deploy-app.py]
    G --> H[HF Space Secrets]
    H --> C
    H --> D
```

## Trust boundaries

1. Public boundary: Internet clients reaching HF Space endpoint.
2. Policy boundary: Nginx route controls before MLflow backend.
3. App boundary: MLflow process bound to localhost and reachable through Nginx.
4. Data boundary: MySQL connection secured with CA-backed TLS.

## Request behavior

```mermaid
sequenceDiagram
    participant U as User
    participant N as Nginx
    participant M as MLflow
    participant DB as MySQL

    alt Anonymous read request
        U->>N: GET/search/list API or UI path
        N->>M: Proxy pass
        M->>DB: SELECT over TLS
        DB-->>M: Result set
        M-->>N: Response
        N-->>U: 200 OK
    else Write request
        U->>N: create/update/delete API
        N->>N: Enforce Basic Auth
        alt Valid credentials
            N->>M: Proxy write operation
            M->>DB: INSERT/UPDATE/DELETE over TLS
            DB-->>M: Success
            M-->>N: 200/201
            N-->>U: Success
        else Invalid or missing credentials
            N-->>U: 401 Unauthorized
        end
    end
```

## Source of truth in code

- Route policy and auth gates: [app/nginx.conf](../app/nginx.conf)
- Runtime bootstrap and process wiring: [app/Dockerfile](../app/Dockerfile)
- CA materialization and connection mutation: [app/mysql_ca.py](../app/mysql_ca.py)
- Deployment secret propagation: [deploy-app.py](../deploy-app.py)
- CI trigger and secret wiring: [.github/workflows/pipeline.yml](../.github/workflows/pipeline.yml)

## Access control matrix

| Endpoint pattern | Method intent | Anonymous | Authenticated admin |
|---|---|---|---|
| `/ajax-api/2.0/mlflow/(experiments|runs)/(create|delete|update)` | mutate tracking state | denied | allowed |
| all other proxied routes (`location /`) | query UI/data/assets and non-blocked APIs | allowed | allowed |

Notes:

- This matrix reflects current implementation, not all potential MLflow APIs.
- Any mutation endpoint not matched by protected regex may remain effectively open.

## Security posture: current vs target

| Area | Current state | Recommended evolution |
|---|---|---|
| Write authorization | Basic auth on selected regex paths | Expand mutation endpoint coverage and adopt token-aware policies |
| Identity integration | Local credential only | OIDC/Auth proxy with group-based RBAC |
| Auditability | Nginx/MLflow logs only | Centralized SIEM ingestion and immutable audit trails |
| Transport controls | MySQL TLS via CA cert | Add cert expiry monitoring and automated rotation workflows |

## Future extensions

1. Token-based write authorization:
   - Require signed service/user tokens on mutation routes.
   - Keep anonymous reads untouched.
2. OIDC/Auth-proxy model:
   - Delegate authn/authz to enterprise IdP.
   - Map groups to MLflow roles for fine-grained policies.
3. Policy hardening:
   - Shift from allow-by-default to explicit allow-list for read endpoints and deny-by-default fallback.
