# resource-monitoring Specification

## Purpose
TBD - created by archiving change add-resource-monitoring. Update Purpose after archive.
## Requirements
### Requirement: Memory Monitoring
The system SHALL collect memory usage from remote servers by executing `free -b` over SSH and reporting total, used, and available memory.

#### Scenario: Memory data collected
- **WHEN** the user runs `cloud-map resources`
- **THEN** each reachable server displays total memory, used memory, available memory, and usage percentage

### Requirement: CPU Monitoring
The system SHALL collect CPU core count via `nproc` and current CPU usage via `vmstat` over SSH.

#### Scenario: CPU data collected
- **WHEN** the user runs `cloud-map resources`
- **THEN** each reachable server displays number of CPU cores and current CPU usage percentage

### Requirement: Disk Monitoring
The system SHALL collect disk partition usage from remote servers by executing `df` over SSH, excluding virtual filesystems (tmpfs, devtmpfs, squashfs).

#### Scenario: Disk data collected
- **WHEN** the user runs `cloud-map resources`
- **THEN** each reachable server displays mount point, total size, used size, and usage percentage for each disk partition

### Requirement: Resource Usage Thresholds
The system SHALL color-code resource usage with thresholds: green below 70%, yellow between 70-90%, and red above 90%.

#### Scenario: High memory usage
- **WHEN** a server's memory usage exceeds 90%
- **THEN** the memory usage is displayed in red in both terminal and PDF output

### Requirement: Resource PDF Export
The `cloud-map resources` command SHALL support the `--pdf` flag to generate a printable PDF report of system resources.

#### Scenario: Resources exported to PDF
- **WHEN** the user runs `cloud-map resources --pdf resources.pdf`
- **THEN** a PDF file is created containing CPU, memory, and disk usage for all servers

