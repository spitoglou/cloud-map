## ADDED Requirements

### Requirement: Inline Log Viewer
The web dashboard SHALL provide an inline log viewer panel that displays log
output for containers and services, fetched on demand from the logs API endpoint.

#### Scenario: Log viewer opens on click
- **WHEN** the user clicks a container or service row in the dashboard
- **THEN** a log viewer panel opens displaying that item's recent logs

#### Scenario: Log viewer controls
- **WHEN** the log viewer is open
- **THEN** it provides a line count selector, a refresh button, and a close button
