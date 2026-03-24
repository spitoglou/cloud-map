# Change: Add Web Monitoring Dashboard

## Why
Cloud Map currently only exposes server health and resource data through the CLI.
A browser-based dashboard would give teams at-a-glance visibility into fleet health
without requiring terminal access, and enable auto-refreshing live monitoring.

## What Changes
- Add a new `cloud-map web` CLI command that starts a FastAPI server (binds to `0.0.0.0:8000` by default)
- Serve a Jinja2-rendered dashboard showing server status, containers, systemd services, and resource usage
- Reuse existing `collector`, `ssh`, `docker`, `systemd`, and `resources` modules for data collection
- Add an API endpoint for AJAX-based live refresh without full page reloads
- Add new `fastapi`, `jinja2`, and `uvicorn` dependencies

## Impact
- Affected specs: new `web-dashboard` capability
- Affected code: `pyproject.toml` (new deps), new `src/cloud_map/web.py`, new `src/cloud_map/templates/` directory, `src/cloud_map/cli.py` (new command)
