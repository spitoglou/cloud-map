# on-demand-logs Specification

## Purpose
TBD - created by archiving change add-on-demand-logs. Update Purpose after archive.
## Requirements
### Requirement: Docker Container Log Retrieval
The system SHALL fetch recent log output from Docker containers on remote servers
via SSH using `docker logs --tail`.

#### Scenario: Fetch container logs
- **WHEN** the user requests logs for a Docker container on a specific server
- **THEN** the system returns the last N lines of that container's log output

#### Scenario: Container not found
- **WHEN** the user requests logs for a container that does not exist
- **THEN** the system returns an error message indicating the container was not found

#### Scenario: Custom line count
- **WHEN** the user requests logs with a specific line count
- **THEN** the system returns exactly that many lines (or fewer if the log is shorter)

### Requirement: Systemd Service Log Retrieval
The system SHALL fetch recent log output from systemd services on remote servers
via SSH using `journalctl -u`.

#### Scenario: Fetch service logs
- **WHEN** the user requests logs for a systemd service on a specific server
- **THEN** the system returns the last N lines of that service's journal output

#### Scenario: Service not found
- **WHEN** the user requests logs for a service that does not exist
- **THEN** the system returns an error message indicating the service was not found

### Requirement: Logs CLI Command
The system SHALL provide a `cloud-map logs <server> <service>` command that prints
log output to the terminal with configurable line count and optional live tailing.

#### Scenario: View recent logs
- **WHEN** the user runs `cloud-map logs web-1 nginx`
- **THEN** the last 100 lines of logs are printed to the terminal

#### Scenario: Custom line count
- **WHEN** the user runs `cloud-map logs web-1 nginx --lines 500`
- **THEN** the last 500 lines are printed

#### Scenario: Follow mode
- **WHEN** the user runs `cloud-map logs web-1 nginx --follow`
- **THEN** the log output streams continuously until interrupted

### Requirement: Logs Web API Endpoint
The system SHALL expose a `GET /api/logs/{server}/{service}` endpoint that returns
log output as plain text.

#### Scenario: Fetch logs via API
- **WHEN** a client sends `GET /api/logs/web-1/nginx?lines=200`
- **THEN** the response is plain text containing the last 200 lines of logs

#### Scenario: Unknown server or service
- **WHEN** a client requests logs for a server or service not in the inventory
- **THEN** the response is a 404 with an error message

#### Scenario: Line count validation
- **WHEN** a client requests more than 10000 lines
- **THEN** the response is a 400 with a validation error

### Requirement: Log Viewer in Web Dashboard
The web dashboard SHALL provide an inline log viewer that opens when clicking a
container or service row, fetching and displaying logs from the API.

#### Scenario: Open log viewer from container row
- **WHEN** the user clicks a container in the Containers tab
- **THEN** a log viewer panel opens showing that container's recent logs

#### Scenario: Open log viewer from service row
- **WHEN** the user clicks a service in the Services tab
- **THEN** a log viewer panel opens showing that service's recent logs

#### Scenario: Refresh and line count controls
- **WHEN** the log viewer is open
- **THEN** the user can change the line count and refresh the logs

