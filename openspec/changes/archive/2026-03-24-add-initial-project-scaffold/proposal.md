# Change: Initial project scaffold for Cloud Map

## Why
The project needs its foundational structure: UV project config, package layout, SSH connectivity, Docker container management, and service health visualization. This establishes the core capabilities that all future work builds on.

## What Changes
- Initialize UV project with Python 3.13 and core dependencies
- Create `cloud_map` package with CLI entry point
- Add server inventory configuration (YAML-based)
- Implement SSH connection management
- Implement Docker container listing and status via SSH
- Implement systemd service status checking via SSH
- Implement service health checking and status reporting
- Support both key-based and password-based SSH authentication
- Add terminal-based visualization of service health
- Persist last known state to local cache for offline queries
- Create `docs/` folder with architecture, capabilities, and configuration documentation
- Add pre-commit hook enforcing documentation updates alongside code changes

## Impact
- Affected specs: `server-connectivity`, `docker-management`, `systemd-management`, `service-health`, `state-cache`, `documentation` (all new)
- Affected code: entire project (greenfield)
