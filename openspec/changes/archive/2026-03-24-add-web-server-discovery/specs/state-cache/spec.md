## MODIFIED Requirements

### Requirement: State Persistence
The system SHALL persist the most recent health and status data for all servers and services — including discovered web server domains — to a local cache file after every successful collection run.

#### Scenario: Cache written after status check
- **WHEN** `cloud-map status`, `cloud-map containers`, `cloud-map services`, or `cloud-map domains` completes
- **THEN** the collected data is written to a local cache file with a timestamp

#### Scenario: Cache includes all collected data
- **WHEN** the cache is written
- **THEN** it contains per-server, per-service health status, container states, systemd states, discovered domains, and the collection timestamp

#### Scenario: Cache round-trip with domains
- **WHEN** server statuses with domain data are saved to cache and loaded back
- **THEN** domain data is fully restored
