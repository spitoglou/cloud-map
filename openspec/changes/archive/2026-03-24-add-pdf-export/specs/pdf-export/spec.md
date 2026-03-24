## ADDED Requirements

### Requirement: PDF Export Flag
All CLI commands SHALL support a `--pdf <path>` option that generates a PDF report at the specified file path.

#### Scenario: Export status to PDF
- **WHEN** the user runs `cloud-map status --pdf report.pdf`
- **THEN** a PDF file is created at `report.pdf` containing the health status table and fleet summary

#### Scenario: Export ping to PDF
- **WHEN** the user runs `cloud-map ping --pdf connectivity.pdf`
- **THEN** a PDF file is created containing the connectivity check results

#### Scenario: Export containers to PDF
- **WHEN** the user runs `cloud-map containers --pdf containers.pdf`
- **THEN** a PDF file is created containing the Docker container listing

#### Scenario: Export services to PDF
- **WHEN** the user runs `cloud-map services --pdf services.pdf`
- **THEN** a PDF file is created containing the systemd service listing

### Requirement: PDF Content Fidelity
The PDF output SHALL contain the same data as the terminal output, including color-coded health indicators, formatted tables, and timestamps.

#### Scenario: PDF includes health colors
- **WHEN** a PDF report is generated
- **THEN** healthy services appear in green, unhealthy in red, degraded in yellow, and unknown in gray

### Requirement: PDF With Cached Data
The `--pdf` flag SHALL work with the `--cached` flag on the `status` command, including the cache age in the PDF.

#### Scenario: Cached status PDF
- **WHEN** the user runs `cloud-map status --cached --pdf report.pdf`
- **THEN** the PDF includes the cached data and a "Last updated" timestamp
