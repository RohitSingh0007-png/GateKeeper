# Cgroups Notes

Raw log of manual cgroup + PostgreSQL backend process validation

---

## Environment

- **Date:** 10/09/2026
- **Team member(s):** Gokul Singh
- **OS / kernel version** (`uname -r`): 6.18.33.2-microsoft-standard-WSL2
- **cgroups v2 confirmed?** (`mount | grep cgroup2` output): cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate)

---

## Part 1 — Manual cgroup with a CPU-heavy process

### 1. Create the test cgroup
Command run:
```
 sudo mkdir /sys/fs/cgroup/test_tenant
 ls /sys/fs/cgroup/test_tenant
```
Observation (what files appeared inside it):
```
cgroup.controllers      cgroup.stat.local       cpu.stat.local       memory.max           memory.swap.events
cgroup.events           cgroup.subtree_control  cpu.weight           memory.min           memory.swap.high
cgroup.freeze           cgroup.threads          cpu.weight.nice      memory.numa_stat     memory.swap.max
cgroup.kill             cgroup.type             io.pressure          memory.oom.group     memory.swap.peak
cgroup.max.depth        cpu.idle                memory.current       memory.peak          pids.current
cgroup.max.descendants  cpu.max                 memory.events        memory.pressure      pids.events
cgroup.pressure         cpu.max.burst           memory.events.local  memory.reclaim       pids.events.local
cgroup.procs            cpu.pressure            memory.high          memory.stat          pids.max
cgroup.stat             cpu.stat                memory.low           memory.swap.current  pids.peak
```

### 2. Start a CPU-heavy process
Command run:
```
yes > /dev/null &
echo $!
```
PID observed: 18160

### 3. CPU usage before any limit (from `top`)
CPU% observed: 100%

### 4. Move PID into cgroup
Command run:
```
sudo sh -c "echo 18160 > /sys/fs/cgroup/test_tenant/cgroup.procs"
```

### 5. Apply `cpu.max`
Value set:
```
sudo sh -c "echo '20000 100000' > /sys/fs/cgroup/test_tenant/cpu.max"
```

### 6. CPU usage after the limit (from `top`)
CPU% observed: 20%
Time taken for the drop to become visible: 1-2 seconds

### 7. Cleanup
Command run:
```
kill 18160
```

**Conclusion for Part 1:**  Moving the `yes` process's PID into the test cgroup and setting `cpu.max` to
`20000 100000` reduced its CPU usage from 100% to approximately 20% within
1-2 seconds, matching the expected 20% cap (20ms allowed per 100ms period).
This confirms that Linux cgroups v2 can enforce a hard CPU limit on an
arbitrary running process, with the kernel applying the restriction almost
immediately after the PID is added to the cgroup and the limit is set.


---

## Part 2 — Real PostgreSQL backend process

### 1. Get backend PID from `psql`
Query run:
```sql
SELECT pg_backend_pid();
```
PID returned: 18311

### 2. Confirming it's a real OS process
Command run:
```
ps aux | grep 18311
```
Output:
```
postgres   18311  0.0  0.1 227104 15824 ?        Ss   21:09   0:00 postgres: 18/main: postgres postgres [local] idle
gokul1     18321  0.0  0.0   4128  2416 pts/2    S+   21:10   0:00 grep --color=auto 18311
```

### 3. Moved PID into cgroup + set limit
Cgroup used:
`cpu.max` value set: '20000 100000' This caps it to 20% of one core (20ms allowed per 100ms period).

### 4. Heavy query — WITH limit applied
Query run: 
```sql
\timing
SELECT count(*) FROM generate_series(1,10000000) a, generate_series(1,50) b;
```
Duration (`\timing` output): 27006.023 ms (00:27.006)

### 5. Heavy query — WITHOUT limit (limit removed)
`cpu.max` reset to: max 100000

Duration (`\timing` output): 4093.614 ms (00:04.094)

### 6. Comparison

| Condition | Query duration |
|---|---|
| With cgroup limit | 27006.023 ms |
| Without cgroup limit | 4093.614 ms |

**Conclusion for Part 2:** With the PostgreSQL backend process (PID 18311) confined to the same 20%
CPU cap, the heavy cross-join query took 27006.023 ms to complete, compared
to 4093.614 ms when the same query was run without any cgroup limit — roughly
6.6x slower under the restricted cgroup. This confirms that a real PostgreSQL
backend process, once its OS-level PID is obtained via pg_backend_pid() and
placed into a cgroup, is subject to the same kernel-enforced CPU throttling
observed in Part 1. This validates the core mechanism the Governor module
will automate: a tenant's database session can be reliably isolated and
resource-limited at the kernel level, independent of anything the database
or application layer does.


---
