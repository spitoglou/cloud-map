# Project Context

## Purpose
Cloud Map is a cloud server administration tool that connects to remote servers via SSH to manage Docker containers, services, and infrastructure. It provides visualization of service availability and health across a fleet of servers.

## Tech Stack
- Python 3.13
- UV (package/project manager)
- SSH (remote server connectivity)
- Docker (container management via remote hosts)

## Project Conventions

### Code Style
- Python 3.13 features encouraged (type hints, match statements, etc.)
- Ruff for linting and formatting
- Type annotations on all public APIs

### Architecture Patterns
- CLI-first interface
- Async SSH connections where beneficial
- Configuration-driven server inventory

### Testing Strategy
- pytest for unit and integration tests
- Mocked SSH for unit tests, real connections for integration

### Git Workflow
- `main` branch is the default
- Feature branches with PR-based merges

## Domain Context
- "Server" refers to remote Linux hosts accessible via SSH
- "Service" refers to a Docker container, systemd unit, or other managed process on a server
- "Health" is determined by service-specific checks (container status, port reachability, process state)

## Important Constraints
- Must work on Windows, macOS, and Linux development machines
- Target servers are Linux-based
- SSH key-based authentication preferred

## External Dependencies
- Remote servers accessible via SSH
- Docker Engine on target servers
