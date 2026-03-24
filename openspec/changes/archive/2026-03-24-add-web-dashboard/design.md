## Context
Cloud Map collects server data via SSH and displays it in Rich tables on the CLI.
Users want a web UI for shared monitoring without terminal access. The dashboard
should feel lightweight and fit the existing architecture rather than introducing
a heavy frontend framework.

## Goals / Non-Goals
- Goals:
  - Serve an HTML dashboard from a single `cloud-map web` command
  - Show the same data views available in the CLI (status, containers, services, resources)
  - Support auto-refresh for live monitoring
  - Keep deployment simple — no Node.js build step, no SPA framework
- Non-Goals:
  - User authentication / multi-tenancy (out of scope for v1)
  - Persistent history / time-series storage
  - WebSocket push (polling is sufficient for v1)

## Decisions
- **FastAPI + Jinja2**: FastAPI for the web framework, Jinja2 for server-side rendered templates.
  Alternatives: Flask (heavier for async), pure HTMX (considered, can add later).
  FastAPI is async-native, which aligns with the existing asyncssh-based collection.
- **Uvicorn**: Standard ASGI server, used as a dependency for `cloud-map web` startup.
- **Single HTML template with sections**: One `dashboard.html` template with tabbed sections
  for status overview, containers, services, and resources. Keeps template count minimal.
- **JSON API endpoint**: `/api/status` returns collected data as JSON for AJAX refresh.
  The Jinja2 template fetches this on a configurable interval to update the page without
  full reload.
- **No database**: Data is collected live on each request or refresh cycle. The existing
  cache module can be used to avoid hammering servers on rapid refreshes.

## Risks / Trade-offs
- **Latency on first load**: Collection over SSH takes seconds. Mitigation: show cached data
  immediately while triggering a background refresh; display a "last updated" timestamp.
- **Concurrent access**: Multiple browser tabs hitting `/api/status` could trigger parallel
  SSH sessions. Mitigation: use the existing cache with a short TTL (e.g. 30s) so only the
  first request triggers collection.
- **New dependencies**: `fastapi`, `jinja2`, `uvicorn` increase the dependency footprint.
  Mitigation: these are well-maintained, widely-used packages.

## Resolved Questions
- **Refresh interval**: Configurable via the UI. The CLI `--refresh` flag sets the initial
  default (e.g. `--refresh 30` for 30 seconds). The dashboard includes a control (dropdown
  or input) that lets users change the interval on the fly — the JS polling loop reads the
  current value from the UI element each cycle.
- **Bind address**: Default to `0.0.0.0` so the dashboard is accessible from other machines
  on the network (common use case: shared team monitoring).
