# web-dashboard Specification

## Purpose
TBD - created by archiving change add-web-dashboard. Update Purpose after archive.
## Requirements
### Requirement: Web Dashboard Server
The system SHALL provide a `cloud-map web` CLI command that starts a FastAPI-based
web server serving an HTML dashboard for monitoring server health and resources.

#### Scenario: Start web server with defaults
- **WHEN** the user runs `cloud-map web`
- **THEN** a web server starts on `0.0.0.0:8000`
- **AND** the dashboard is accessible at `http://<host>:8000/`

#### Scenario: Custom host and port
- **WHEN** the user runs `cloud-map web --host 127.0.0.1 --port 9090`
- **THEN** the server binds to `127.0.0.1:9090`

### Requirement: Dashboard Overview Page
The system SHALL render a Jinja2 HTML template showing a unified view of all servers
with their health status, Docker containers, systemd services, and system resources.

#### Scenario: Dashboard displays server health
- **WHEN** the user opens the dashboard in a browser
- **THEN** each configured server is shown with its reachability and service health summary

#### Scenario: Dashboard displays resource usage
- **WHEN** the user opens the dashboard in a browser
- **THEN** CPU, memory, and disk usage are displayed for each reachable server

### Requirement: Live Refresh via JSON API
The system SHALL expose a `GET /api/status` endpoint returning server statuses
as JSON, and the dashboard SHALL auto-refresh by polling this endpoint.

#### Scenario: JSON API returns current status
- **WHEN** a client sends `GET /api/status`
- **THEN** the response is a JSON array of server status objects

#### Scenario: Auto-refresh updates the page
- **WHEN** the dashboard is open and the refresh interval elapses
- **THEN** the page updates with fresh data from `/api/status` without a full reload

### Requirement: UI-Configurable Refresh Interval
The dashboard SHALL provide a UI control allowing the user to change the auto-refresh
interval without restarting the server. The CLI `--refresh` flag sets the initial default.

#### Scenario: User changes refresh interval in the UI
- **WHEN** the user selects a different refresh interval from the dashboard control
- **THEN** the polling loop immediately adopts the new interval

#### Scenario: CLI sets initial refresh default
- **WHEN** the user runs `cloud-map web --refresh 60`
- **THEN** the dashboard loads with a 60-second refresh interval by default

### Requirement: Cache-Aware Collection
The system SHALL use the existing state cache to avoid redundant SSH connections when
multiple requests arrive within a short time window.

#### Scenario: Cached data served within TTL
- **WHEN** data was collected less than 30 seconds ago
- **AND** a new request arrives
- **THEN** the cached data is returned without triggering new SSH connections

#### Scenario: Stale cache triggers fresh collection
- **WHEN** the cache is older than 30 seconds
- **AND** a new request arrives
- **THEN** fresh data is collected via SSH and the cache is updated

### Requirement: Domains Tab
The web dashboard SHALL include a "Domains" tab that displays discovered web server
domains grouped by server in collapsible sections, showing domain name, web server
type, and configuration file path.

#### Scenario: Domains tab with data
- **WHEN** servers have discovered domains
- **THEN** the Domains tab shows them grouped by server with collapsible sections

#### Scenario: No domains discovered
- **WHEN** no servers have web server discovery configured or no domains are found
- **THEN** the Domains tab shows an empty state message

### Requirement: Inline Log Viewer
The web dashboard SHALL provide an inline log viewer panel that displays log
output for containers and services, fetched on demand from the logs API endpoint.

#### Scenario: Log viewer opens on click
- **WHEN** the user clicks a container or service row in the dashboard
- **THEN** a log viewer panel opens displaying that item's recent logs

#### Scenario: Log viewer controls
- **WHEN** the log viewer is open
- **THEN** it provides a line count selector, a refresh button, and a close button

