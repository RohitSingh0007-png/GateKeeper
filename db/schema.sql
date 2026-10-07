-- plan_tiers: defines the CPU/memory quota for each subscription tier.
-- The Governor reads this to know what cpu.max / memory.max to apply
-- when assigning a tenant's backend process to its cgroup.
-- ---------------------------------------------------------------------
CREATE TABLE plan_tiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,       -- e.g. 'basic', 'pro', 'enterprise'
    cpu_quota_percent INTEGER NOT NULL,     -- e.g. 20 means 20% of one core
    memory_limit_mb INTEGER NOT NULL,       -- e.g. 256
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- tenants: one row per simulated "business" using the shared database.
-- ---------------------------------------------------------------------
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,             -- e.g. 'Acme Corp'
    plan_tier_id INTEGER NOT NULL REFERENCES plan_tiers(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- users: login credentials for both tenant users and the admin user.
-- role distinguishes 'tenant' vs 'admin'. tenant_id is NULL for admin.
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),   -- NULL for admin users
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'tenant', -- 'tenant' or 'admin'
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- usage_events: periodic CPU/memory usage snapshots per tenant,
-- read from cgroup stat files by the Governor's monitoring function.
-- Feeds the admin dashboard's live usage chart.
-- ---------------------------------------------------------------------
CREATE TABLE usage_events (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    cpu_percent REAL NOT NULL,
    memory_used_mb REAL NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- throttle_events: logged whenever the Governor detects a tenant's
-- cgroup actually throttled a process (via cpu.stat's nr_throttled).
-- Feeds the admin dashboard's throttle-event log.
-- ---------------------------------------------------------------------
CREATE TABLE throttle_events (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    throttled_ms INTEGER NOT NULL,          -- duration throttled, in ms
    occurred_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- Seed data: starter plan tiers, so tenants can be created against them
-- immediately. Adjust values once demo requirements are finalized.
-- ---------------------------------------------------------------------
INSERT INTO plan_tiers (name, cpu_quota_percent, memory_limit_mb) VALUES
    ('basic', 20, 256),
    ('pro', 50, 1024),
    ('enterprise', 100, 4096);
