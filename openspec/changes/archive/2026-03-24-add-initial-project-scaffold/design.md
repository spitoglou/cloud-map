## Context
Greenfield Python 3.13 project. Needs to SSH into remote servers, inspect Docker containers and other services, and present health status visually. Must work from Windows/macOS/Linux dev machines targeting Linux servers.

## Goals / Non-Goals
- Goals:
  - Simple CLI tool to check and display server/service health
  - YAML-based server inventory
  - SSH-based remote execution (no agents on target servers)
  - Docker container status via `docker` CLI over SSH
  - Systemd service status via `systemctl` over SSH
  - Rich terminal output for health visualization
  - Both key-based and password-based SSH authentication
- Non-Goals:
  - Web UI (future consideration)
  - Agent-based monitoring (push model)
  - Alerting or notifications
  - Metrics storage or time-series data

## Decisions
- **asyncssh** for SSH connections: mature, async-native, pure Python (no libssh dependency issues on Windows)
- **Rich** for terminal visualization: tables, color-coded status, tree views
- **PyYAML** for configuration: simple, well-known
- **Click** for CLI: composable, well-documented
- **Package layout**: `src/cloud_map/` (src layout per UV convention)

## Risks / Trade-offs
- asyncssh vs paramiko: asyncssh is async-native but less battle-tested; paramiko is synchronous but more widely used → choosing asyncssh for modern async patterns, can fallback to paramiko if issues arise
- Docker inspection via SSH `docker` CLI vs Docker API over SSH tunnel → CLI is simpler, no extra dependencies; API gives structured data → start with CLI, upgrade if needed

## Open Questions
- ~~Should we support systemd service checks in v1 or just Docker?~~ → Yes, both in v1
- ~~Password-based SSH auth: support or defer?~~ → Yes, support both key-based and password-based
