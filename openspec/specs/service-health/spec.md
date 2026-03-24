# service-health Specification

## Purpose
TBD - created by archiving change add-initial-project-scaffold. Update Purpose after archive.
## Requirements
### Requirement: Health Status Model
The system SHALL define service health as one of: healthy, unhealthy, degraded, or unknown. Each service MUST map to exactly one health status.

#### Scenario: Healthy Docker container
- **WHEN** a Docker container is running and its health check passes
- **THEN** the service health is reported as "healthy"

#### Scenario: Healthy systemd service
- **WHEN** a systemd service is in the "active (running)" state
- **THEN** the service health is reported as "healthy"

#### Scenario: Unreachable server
- **WHEN** a server cannot be reached via SSH
- **THEN** all services on that server are reported as "unknown"

### Requirement: Health Visualization
The system SHALL display a color-coded terminal table showing all servers, their services, and health status using Rich.

#### Scenario: Status overview
- **WHEN** the user runs `cloud-map status`
- **THEN** a table is displayed with servers as rows, services as entries, and color-coded health indicators (green=healthy, red=unhealthy, yellow=degraded, gray=unknown)

### Requirement: Health Aggregation
The system SHALL aggregate health across all servers to provide a fleet-level summary.

#### Scenario: Fleet summary
- **WHEN** health data is collected from all servers
- **THEN** the system displays total counts of healthy, unhealthy, degraded, and unknown services

