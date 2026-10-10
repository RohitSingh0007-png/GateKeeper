# cgroups v2 Validation Notes

Independent manual validation of the mechanism Gatekeeper relies on: a Linux
cgroup (v2) can throttle a real PostgreSQL backend process, identified by
`pg_backend_pid()`.

## Environment

- Ubuntu with cgroups v2 (`stat -fc %T /sys/fs/cgroup/` returns `cgroup2fs`)
- `cpu` and `memory` controllers available and enabled for child cgroups
- PostgreSQL 18

## Method

1. Created a test cgroup: `sudo mkdir /sys/fs/cgroup/gatekeeper-test`
2. Set a CPU limit of 20% of one core: `echo "20000 100000" | sudo tee .../cpu.max`
   (`cpu.max` is `quota period` in microseconds: 20 ms of CPU per 100 ms window)
3. Moved a process into the cgroup by writing its PID to `cgroup.procs`
4. Measured behaviour with `top` and with the kernel's own counters in `cpu.stat`

## Experiment 1: CPU-bound process (`yes > /dev/null`)

| Condition | %CPU (top) |
|---|---|
| No limit | 100% |
| In cgroup, `cpu.max = 20000 100000` | 20% |

Over a ~5 s window, `cpu.stat` showed `nr_periods` and `nr_throttled` both
rising by 197 (throttled in every window), with ~3.95 s of CPU used in ~19.7 s
of wall-clock time, which is about 20%.

## Experiment 2: real PostgreSQL backend

The backend PID was obtained from `SELECT pg_backend_pid();` in a `psql`
session. The query used was:

    SELECT count(*) FROM generate_series(1, 30000000);

| Condition | Query time |
|---|---|
| Backend outside the cgroup (baseline) | 5.9 s |
| Backend inside the 20% cgroup | 45.4 s and 49.7 s (two runs) |

Per-run deltas from `cpu.stat` for the 49.7 s run:

| Counter | Delta |
|---|---|
| `usage_usec` | +9.95 s of CPU |
| `nr_periods` | +499 windows (~49.9 s) |
| `nr_throttled` | +497 windows (99.6%) |
| `throttled_usec` | +39.7 s paused (~80% of the time) |

CPU share = 9.95 s / 49.9 s, about 19.9%, so the kernel enforced the 20% limit
accurately. The throttled run used more CPU time (~10 s) than the unthrottled
run took in wall time (5.9 s). The cause was not investigated.

## Findings relevant to the Governor

- **The mechanism works on a real Postgres backend.** The limit is enforced by
  the kernel, and the backend process is unaware of it.
- **`cpu.stat` counters are cumulative.** CPU % must be computed from two
  samples: `delta(usage_usec) / delta(wall-clock time)`.
- **`nr_throttled` and `throttled_usec` measure different things** (windows
  hit vs. total time lost), so the monitor should track both.
- **cgroups live in memory and disappear on reboot**, so cgroup creation must
  be idempotent (create if not exists).
- **Moving a process into a cgroup requires root**, even though Postgres
  backends run as the `postgres` user, so the Governor needs root or delegated
  permissions.
- **The backend must stay on one session.** `pg_backend_pid()` is only valid
  for that connection, which is why Gatekeeper uses session pooling, not
  transaction pooling.

