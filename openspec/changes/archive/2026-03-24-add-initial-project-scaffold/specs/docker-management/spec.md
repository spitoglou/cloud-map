## ADDED Requirements

### Requirement: Docker Container Listing
The system SHALL list Docker containers on remote servers by executing `docker ps` over SSH and parsing the output.

#### Scenario: List running containers
- **WHEN** the user runs `cloud-map containers`
- **THEN** the system displays all running containers across all reachable servers with name, image, status, and ports

#### Scenario: Server without Docker
- **WHEN** a server does not have Docker installed
- **THEN** the system reports that Docker is unavailable on that server and continues

### Requirement: Container Status Parsing
The system SHALL parse Docker container status including running, exited, restarting, and health check states.

#### Scenario: Container with health check
- **WHEN** a container has a Docker health check configured
- **THEN** the system reports the health status (healthy, unhealthy, starting) alongside the container state
