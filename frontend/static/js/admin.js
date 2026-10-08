// Admin dashboard: refresh tenant usage from the usage endpoint
// (GET /admin/usage, shape defined in docs/interface-contract.md).
// Phase III can call refreshUsage() on a timer and draw the chart from the same samples.
(function () {
    "use strict";

    const table = document.getElementById("tenant-table");
    if (!table) return;

    const refreshButton = document.getElementById("usage-refresh");
    const errorBox = document.getElementById("usage-error");
    const updated = document.getElementById("usage-updated");
    const warnRatio = Number(table.dataset.warnRatio) || 0.9;

    // Keep in sync with usage_status() on the server and status_badge in macros/ui.html.
    const STATUS = {
        healthy: { label: "Healthy", tone: "success" },
        warning: { label: "Near limit", tone: "warning" },
        throttled: { label: "Throttled", tone: "danger" },
        idle: { label: "Idle", tone: "neutral" },
    };

    function statusFor(sample, cpuQuota, memoryLimit) {
        if (!sample) return "idle";
        if (sample.throttled_ms > 0) return "throttled";
        if (sample.cpu_percent >= cpuQuota * warnRatio || sample.memory_used_mb >= memoryLimit * warnRatio) {
            return "warning";
        }
        return "healthy";
    }

    function updateMeter(row, field, used, limit, unit, decimals) {
        const text = row.querySelector(`[data-field="${field}-text"]`);
        const bar = row.querySelector(`[data-field="${field}-bar"]`);
        let pct = 0;
        let tone = "idle";
        if (used == null) {
            text.textContent = "No session";
        } else {
            pct = limit ? Math.min((used / limit) * 100, 100) : 0;
            tone = pct >= 100 ? "danger" : pct >= warnRatio * 100 ? "warning" : "ok";
            text.textContent = `${used.toFixed(decimals)}${unit} / ${limit}${unit}`;
        }
        bar.setAttribute("aria-valuenow", String(Math.round(pct)));
        bar.firstElementChild.className = `meter__fill meter__fill--${tone}`;
        bar.firstElementChild.style.width = `${pct.toFixed(1)}%`;
    }

    function setStat(field, value) {
        const el = document.querySelector(`[data-stat="${field}"]`);
        if (el) el.textContent = value;
    }

    function applyUsage(samples) {
        const byTenant = new Map(samples.map((sample) => [String(sample.tenant_id), sample]));
        let active = 0;
        let throttled = 0;
        let cpuTotal = 0;

        table.querySelectorAll("tbody tr[data-tenant-id]").forEach((row) => {
            const sample = byTenant.get(row.dataset.tenantId) || null;
            const cpuQuota = Number(row.dataset.cpuQuota);
            const memoryLimit = Number(row.dataset.memoryLimit);

            updateMeter(row, "cpu", sample && sample.cpu_percent, cpuQuota, "%", 1);
            updateMeter(row, "memory", sample && sample.memory_used_mb, memoryLimit, " MB", 0);
            row.querySelector('[data-field="throttled"]').textContent =
                sample ? `${GK.formatNumber(sample.throttled_ms)} ms` : "—";

            const status = statusFor(sample, cpuQuota, memoryLimit);
            const badge = row.querySelector('[data-field="status"]');
            badge.textContent = STATUS[status].label;
            badge.className = `badge badge--${STATUS[status].tone}`;

            if (sample) {
                active += 1;
                cpuTotal += sample.cpu_percent;
            }
            if (status === "throttled") throttled += 1;
        });

        setStat("active", active);
        setStat("throttled", throttled);
        setStat("avg-cpu", active ? `${(cpuTotal / active).toFixed(1)}%` : "—");
        document.querySelector('[data-stat-card="throttled"]')?.classList.toggle("stat--danger", throttled > 0);

        const latest = samples.map((sample) => sample.timestamp).sort().pop();
        if (latest) {
            updated.setAttribute("datetime", latest);
            updated.textContent = GK.formatTime(latest);
        }
    }

    async function refreshUsage() {
        GK.setBusy(refreshButton, true, "Refreshing…");
        try {
            const samples = await GK.fetchJSON(table.dataset.usageUrl);
            applyUsage(Array.isArray(samples) ? samples : []);
            errorBox.hidden = true;
        } catch (error) {
            errorBox.textContent = `Couldn't refresh usage: ${error.message}`;
            errorBox.hidden = false;
        } finally {
            GK.setBusy(refreshButton, false);
        }
    }

    refreshButton.addEventListener("click", refreshUsage);

    // Exposed for Phase III (polling and the live chart).
    window.GKAdmin = { refreshUsage, applyUsage };
})();
