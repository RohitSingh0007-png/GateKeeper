import os

CGROUP_ROOT = "/sys/fs/cgroup"
CPU_PERIOD_US = 100000


def create_cgroup(tenant_id: str, cpu_quota_percent: int) -> str:
    path = os.path.join(CGROUP_ROOT, f"gatekeeper-tenant_{tenant_id}")
    os.makedirs(path, exist_ok=True)

    quota_us = cpu_quota_percent * CPU_PERIOD_US // 100
    with open(os.path.join(path, "cpu.max"), "w") as f:
        f.write(f"{quota_us} {CPU_PERIOD_US}")

    return path


if __name__ == "__main__":
    print(create_cgroup("1", 20))

