## 1. Log Fetching Module
- [x] 1.1 Create `src/cloud_map/logs.py`
- [x] 1.2 Implement `fetch_docker_logs(ssh, server, container, lines)` using `docker logs --tail`
- [x] 1.3 Implement `fetch_systemd_logs(ssh, server, service, lines)` using `journalctl -u`
- [x] 1.4 Handle errors gracefully (container not found, permission denied, etc.)

## 2. CLI Command
- [x] 2.1 Add `cloud-map logs <server> <service>` command to `cli.py`
- [x] 2.2 Add `--lines` option (default 100)
- [x] 2.3 Add `--follow` flag for live tailing
- [x] 2.4 Auto-detect service type (docker vs systemd) from cached/live status data

## 3. Web API
- [x] 3.1 Add `GET /api/logs/{server}/{service}` endpoint to `web.py`
- [x] 3.2 Accept `lines` query parameter (default 100, max 10000)
- [x] 3.3 Return plain text response with appropriate content type
- [x] 3.4 Return error messages for unknown servers/services

## 4. Web Dashboard
- [x] 4.1 Add log viewer modal/panel to `dashboard.html`
- [x] 4.2 Wire click handlers on container and service rows to open log viewer
- [x] 4.3 Add line count selector and refresh button in the log viewer
- [x] 4.4 Display logs in monospace pre-formatted block with auto-scroll to bottom

## 5. Documentation & Testing
- [x] 5.1 Update `README.md` with logs command usage
- [x] 5.2 Update `docs/capabilities.md` and `docs/architecture.md`
- [x] 5.3 Add unit tests for log fetching functions
- [x] 5.4 Add web API test for logs endpoint
