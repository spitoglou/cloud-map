## ADDED Requirements

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
