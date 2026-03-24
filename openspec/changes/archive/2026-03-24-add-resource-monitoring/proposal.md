# Change: Add system resource monitoring

## Why
Users need visibility into CPU, memory, and disk usage across their server fleet alongside service health.

## What Changes
- Add `cloud-map resources` command showing CPU cores/usage, memory, and disk space
- Collect resource data via SSH (`free`, `nproc`, `vmstat`, `df`) in a single round-trip
- Color-coded thresholds: green (<70%), yellow (70-90%), red (>90%)
- PDF export support via `--pdf`
- Resource data included in cache for offline queries

## Impact
- Affected specs: `resource-monitoring` (new)
- Affected code: new `resources.py`, updated `models.py`, `collector.py`, `cache.py`, `display.py`, `pdf.py`, `cli.py`
