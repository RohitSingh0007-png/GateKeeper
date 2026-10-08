"""
DEVELOPMENT-ONLY sample data for frontend/dev_server.py.

- Plan tiers mirror the seed rows in db/schema.sql.
- Tenants and users follow the shape of the tenants/users tables.
- Customers and orders have no tables in db/schema.sql yet, so this small
  dataset stands in for them until the backend provides real data.

Not used by the production backend.
"""

# Mirrors the INSERT INTO plan_tiers seed rows in db/schema.sql.
PLAN_TIERS = {
    "basic": {"cpu_quota_percent": 20, "memory_limit_mb": 256},
    "pro": {"cpu_quota_percent": 50, "memory_limit_mb": 1024},
    "enterprise": {"cpu_quota_percent": 100, "memory_limit_mb": 4096},
}

# tenants table: id -> name and plan tier.
TENANTS = {
    1: {"name": "Acme Corp", "plan": "basic"},
    2: {"name": "Globex", "plan": "pro"},
    3: {"name": "Initech", "plan": "basic"},
    4: {"name": "Umbrella Labs", "plan": "enterprise"},
}

# Tenants with an open database session in this dev scenario.
# Umbrella Labs has none, so the UI's idle state can be checked.
ACTIVE_TENANT_IDS = {1, 2, 3}

# Development test accounts. Plain-text passwords are acceptable here ONLY
# because this is local sample data; the real backend stores bcrypt hashes
# in users.password_hash.
DEV_USERS = {
    "acme": {"password": "acme-dev", "role": "tenant", "tenant_id": 1},
    "globex": {"password": "globex-dev", "role": "tenant", "tenant_id": 2},
    "initech": {"password": "initech-dev", "role": "tenant", "tenant_id": 3},
    "umbrella": {"password": "umbrella-dev", "role": "tenant", "tenant_id": 4},
    "admin": {"password": "admin-dev", "role": "admin", "tenant_id": None},
}

CUSTOMERS = {
    1: [
        {"id": 101, "name": "Asha Rao", "email": "asha.rao@example.com", "status": "active", "created_at": "2026-06-14"},
        {"id": 102, "name": "Rohit Negi", "email": "rohit.negi@example.com", "status": "active", "created_at": "2026-07-02"},
        {"id": 103, "name": "Meera Joshi", "email": "meera.joshi@example.com", "status": "active", "created_at": "2026-07-19"},
        {"id": 104, "name": "Karan Bisht", "email": "karan.bisht@example.com", "status": "inactive", "created_at": "2026-08-05"},
        {"id": 105, "name": "Priya Thapa", "email": "priya.thapa@example.com", "status": "active", "created_at": "2026-09-11"},
    ],
    2: [
        {"id": 201, "name": "Neha Rawat", "email": "neha.rawat@example.com", "status": "active", "created_at": "2026-05-21"},
        {"id": 202, "name": "Vikram Singh", "email": "vikram.singh@example.com", "status": "active", "created_at": "2026-06-30"},
        {"id": 203, "name": "Ananya Gusain", "email": "ananya.gusain@example.com", "status": "inactive", "created_at": "2026-08-17"},
        {"id": 204, "name": "Dev Kandpal", "email": "dev.kandpal@example.com", "status": "active", "created_at": "2026-09-03"},
    ],
    3: [
        {"id": 301, "name": "Ishaan Mehra", "email": "ishaan.mehra@example.com", "status": "active", "created_at": "2026-07-08"},
        {"id": 302, "name": "Tara Bhandari", "email": "tara.bhandari@example.com", "status": "active", "created_at": "2026-08-22"},
        {"id": 303, "name": "Arjun Pant", "email": "arjun.pant@example.com", "status": "active", "created_at": "2026-09-26"},
    ],
    4: [],
}

ORDERS = {
    1: [
        {"id": 1001, "customer": "Asha Rao", "amount": 2400.00, "status": "delivered", "created_at": "2026-08-04"},
        {"id": 1002, "customer": "Rohit Negi", "amount": 860.50, "status": "delivered", "created_at": "2026-08-19"},
        {"id": 1003, "customer": "Meera Joshi", "amount": 5120.00, "status": "delivered", "created_at": "2026-08-28"},
        {"id": 1004, "customer": "Priya Thapa", "amount": 1299.00, "status": "shipped", "created_at": "2026-09-09"},
        {"id": 1005, "customer": "Asha Rao", "amount": 3450.00, "status": "paid", "created_at": "2026-09-21"},
        {"id": 1006, "customer": "Karan Bisht", "amount": 640.00, "status": "refunded", "created_at": "2026-09-27"},
        {"id": 1007, "customer": "Meera Joshi", "amount": 1875.25, "status": "pending", "created_at": "2026-10-04"},
        {"id": 1008, "customer": "Rohit Negi", "amount": 990.00, "status": "pending", "created_at": "2026-10-07"},
    ],
    2: [
        {"id": 2001, "customer": "Neha Rawat", "amount": 3150.00, "status": "delivered", "created_at": "2026-08-12"},
        {"id": 2002, "customer": "Vikram Singh", "amount": 740.00, "status": "delivered", "created_at": "2026-09-01"},
        {"id": 2003, "customer": "Dev Kandpal", "amount": 4520.00, "status": "shipped", "created_at": "2026-09-24"},
        {"id": 2004, "customer": "Neha Rawat", "amount": 1210.00, "status": "pending", "created_at": "2026-10-06"},
    ],
    3: [
        {"id": 3001, "customer": "Ishaan Mehra", "amount": 2200.00, "status": "delivered", "created_at": "2026-08-30"},
        {"id": 3002, "customer": "Tara Bhandari", "amount": 980.00, "status": "paid", "created_at": "2026-09-18"},
        {"id": 3003, "customer": "Arjun Pant", "amount": 1640.00, "status": "pending", "created_at": "2026-10-05"},
    ],
    4: [],
}
