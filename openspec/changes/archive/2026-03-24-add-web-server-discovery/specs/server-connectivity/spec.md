## MODIFIED Requirements

### Requirement: Server Inventory Configuration
The system SHALL load server definitions from a YAML configuration file. Each server entry MUST include a hostname and MAY include port, username, SSH key path, password, systemd_services, systemd_exclude, and an optional `webservers` field. The `webservers` field can be a list of overrides (specifying type and custom config_path) or `false` to disable auto-detection for that server.

#### Scenario: Valid inventory loaded
- **WHEN** a valid YAML inventory file exists at the configured path
- **THEN** all server entries are parsed with hostname, port, username, and key path

#### Scenario: Missing inventory file
- **WHEN** the inventory file does not exist
- **THEN** the system reports a clear error and exits gracefully

#### Scenario: Load inventory with webservers overrides
- **WHEN** the inventory YAML includes a server with `webservers` list entries
- **THEN** each entry is parsed into a `WebServerConfig` with type and optional config_path

#### Scenario: Load inventory with webservers disabled
- **WHEN** a server entry has `webservers: false`
- **THEN** web server auto-detection is disabled for that server

#### Scenario: Load inventory without webservers field
- **WHEN** a server entry has no `webservers` field
- **THEN** web server auto-detection proceeds with default paths
