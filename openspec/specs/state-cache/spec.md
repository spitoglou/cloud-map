# state-cache Specification

## Purpose
TBD - created by archiving change add-initial-project-scaffold. Update Purpose after archive.
## Requirements
### Requirement: State Persistence
The system SHALL persist the most recent health and status data for all servers and services to a local cache file after every successful collection run.

#### Scenario: Cache written after status check
- **WHEN** `cloud-map status`, `cloud-map containers`, or `cloud-map services` completes
- **THEN** the collected data is written to a local cache file with a timestamp

#### Scenario: Cache includes all collected data
- **WHEN** the cache is written
- **THEN** it contains per-server, per-service health status, container states, systemd states, and the collection timestamp

### Requirement: Offline Status Query
The system SHALL provide a way to display the last known state without connecting to any server.

#### Scenario: View cached status
- **WHEN** the user runs `cloud-map status --cached`
- **THEN** the system displays the last known health data from the cache with the timestamp of when it was collected

#### Scenario: No cache available
- **WHEN** the user requests cached status but no cache file exists
- **THEN** the system reports that no cached data is available and suggests running a live check

### Requirement: Cache Staleness Indicator
The system SHALL indicate the age of cached data when displaying it, so the user knows how fresh the information is.

#### Scenario: Cache age displayed
- **WHEN** cached data is displayed
- **THEN** the output includes a human-readable age (e.g., "Last updated: 2 hours ago")

