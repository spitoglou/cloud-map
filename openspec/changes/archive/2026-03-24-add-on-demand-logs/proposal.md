# Change: Add On-Demand Log Viewing for Containers and Services

## Why
When a container or service shows as unhealthy or degraded, the first thing an
operator needs is logs. Currently they must SSH into the server manually and run
`docker logs` or `journalctl`. Surfacing logs on demand through both the CLI and
web dashboard removes that friction and keeps troubleshooting within Cloud Map.

## What Changes
- Add a new `src/cloud_map/logs.py` module that fetches logs via SSH using
  `docker logs` (containers) and `journalctl -u` (systemd services)
- Add a `cloud-map logs` CLI command that takes a server name and service name,
  prints the last N lines of logs
- Add a `GET /api/logs/{server}/{service}` endpoint to the web API
- Add a log viewer panel to the web dashboard — click a container or service row
  to fetch and display its logs inline
- Support configurable line count (`--lines` / `?lines=` parameter, default 100)
- Support `--follow` in the CLI for tailing (not in the web UI)

## Impact
- Affected specs: new `on-demand-logs`, modified `web-dashboard` (log viewer)
- Affected code: new `src/cloud_map/logs.py`, `web.py` (new endpoint), `cli.py`
  (new command), `dashboard.html` (log viewer UI)
