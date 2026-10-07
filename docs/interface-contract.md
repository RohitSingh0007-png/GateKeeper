# Interface Contract

---

## Governor.get_connection(tenant_id: str)

Returns a `psycopg2` connection object, pooled per tenant (**session pooling** — the same connection/backend process is retained for the tenant's session, never reused by a different tenant mid-session).

On first connection for a tenant, the Governor looks up the tenant's plan tier and CPU/memory limits from the `tenants` and `plan_tiers` tables (see [`db/schema.sql`](../db/schema.sql)), and assigns the connection's real PostgreSQL backend PID (via `pg_backend_pid()`) into that tenant's Linux cgroup accordingly.

**On failure:** raises an exception (`GovernorConnectionError` or similar) if the tenant cannot be found, the database is unreachable, or the cgroup assignment fails. Callers (the backend) must catch this and respond with an appropriate error rather than letting it propagate as an unhandled 500.

---

## Governor.release_connection(tenant_id: str, conn)

Returns a connection to the tenant's pool once the backend is done using it for a request. Must be called after every `get_connection` to avoid exhausting the pool. Does not remove the PID from its cgroup — the cgroup assignment persists for the connection's lifetime, not just a single request.

---

## Governor.get_tenant_usage(tenant_id: str) -> dict

Reads the tenant's current `cpu.stat` and `memory.current` from its cgroup and returns:
```json
{
  "tenant_id": "string",
  "cpu_percent": 0.0,
  "memory_used_mb": 0.0,
  "throttled_ms": 0,
  "timestamp": "ISO8601 string"
}
```
Used internally by the Governor's background monitor to write rows into the `usage_events` and `throttle_events` tables (see [`db/schema.sql`](../db/schema.sql)), which the admin dashboard reads from.

---

## GET /admin/usage

Returns JSON, sourced from the `usage_events` and `throttle_events` tables:
```json
[
  {
    "tenant_id": "string",
    "cpu_percent": 0.0,
    "memory_used_mb": 0.0,
    "throttled_ms": 0,
    "timestamp": "ISO8601 string"
  }
]
```

---

## Notes

- Thread-safety: the Governor's internal per-tenant pool registry must be safe for concurrent access, since FastAPI handles multiple tenants' requests concurrently. Callers do not need to add their own locking.
- Schema reference: all tenant, plan-tier, and usage data referenced above lives in [`db/schema.sql`](../db/schema.sql) — `tenants`, `plan_tiers`, `users`, `usage_events`, `throttle_events`.
