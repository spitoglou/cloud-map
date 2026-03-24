## ADDED Requirements

### Requirement: Systemd Service Auto-Discovery
The system SHALL auto-discover all running systemd services on remote servers by executing `systemctl list-units --type=service` over SSH when no explicit service list is configured.

#### Scenario: Auto-discover all services
- **WHEN** the user runs `cloud-map services` and `systemd_services` is empty
- **THEN** the system discovers and displays all running systemd services on each reachable server

#### Scenario: Explicit service list
- **WHEN** the user runs `cloud-map services` and `systemd_services` is populated
- **THEN** the system checks only the explicitly listed services via `systemctl show`

#### Scenario: Server without systemd
- **WHEN** a server does not use systemd
- **THEN** the system reports that systemd is unavailable on that server and continues

### Requirement: Systemd Exclude Patterns
The system SHALL support glob-based exclude patterns via the `systemd_exclude` configuration field to filter out unwanted services during auto-discovery.

#### Scenario: Exclude by glob pattern
- **WHEN** `systemd_exclude` contains `"systemd-*"` and auto-discovery is active
- **THEN** all services matching `systemd-*` (e.g., `systemd-journald`, `systemd-logind`) are excluded from the results

#### Scenario: Exclude exact match
- **WHEN** `systemd_exclude` contains `"dbus"` and auto-discovery is active
- **THEN** the `dbus` service is excluded from the results

#### Scenario: Exclude ignored with explicit list
- **WHEN** `systemd_services` is populated
- **THEN** `systemd_exclude` is ignored

### Requirement: Systemd Service Status Parsing
The system SHALL parse systemd service states including active, inactive, failed, and activating.

#### Scenario: Active service
- **WHEN** a systemd service is in the "active (running)" state
- **THEN** the system reports it as healthy

#### Scenario: Failed service
- **WHEN** a systemd service is in the "failed" state
- **THEN** the system reports it as unhealthy
