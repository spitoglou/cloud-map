## 1. Project Setup
- [x] 1.1 Initialize UV project with `pyproject.toml` (Python 3.13, src layout)
- [x] 1.2 Add core dependencies: asyncssh, click, rich, pyyaml
- [x] 1.3 Add dev dependencies: pytest, ruff
- [x] 1.4 Create `src/cloud_map/__init__.py` and `src/cloud_map/cli.py` entry point

## 2. Server Connectivity
- [x] 2.1 Create YAML-based server inventory schema and loader (`config.py`)
- [x] 2.2 Implement SSH connection manager with key and password auth (`ssh.py`)
- [x] 2.3 Add `cloud-map ping` command to test connectivity to all servers
- [x] 2.4 Write tests for config loading and SSH connection

## 3. Docker Management
- [x] 3.1 Implement Docker container listing via SSH (`docker.py`)
- [x] 3.2 Implement container status/health parsing
- [x] 3.3 Add `cloud-map containers` command to list containers across servers
- [x] 3.4 Write tests for Docker output parsing

## 4. Systemd Management
- [x] 4.1 Implement systemd service listing via SSH (`systemd.py`)
- [x] 4.2 Implement systemd service status parsing
- [x] 4.3 Add `cloud-map services` command to list systemd services across servers
- [x] 4.4 Write tests for systemd output parsing

## 5. State Cache
- [x] 5.1 Implement cache storage (write last known state to JSON file after collection) (`cache.py`)
- [x] 5.2 Implement cache loading and staleness calculation
- [x] 5.3 Add `--cached` flag to `cloud-map status` to display last known state offline
- [x] 5.4 Write tests for cache read/write and staleness display

## 6. Documentation
- [x] 6.1 Create `docs/architecture.md` (system design, components, data flow, caching)
- [x] 6.2 Create `docs/capabilities.md` (CLI commands, flags, usage examples)
- [x] 6.3 Create `docs/configuration.md` (inventory file format, options, examples)
- [x] 6.4 Add pre-commit hook that rejects `src/` changes without accompanying `docs/` changes
- [x] 6.5 Add `pre-commit` dev dependency and hook configuration

## 7. Service Health
- [x] 7.1 Define health check model and status types (`models.py`)
- [x] 7.2 Implement health aggregation across servers (Docker + systemd)
- [x] 7.3 Add `cloud-map status` command with Rich table visualization
- [x] 7.4 Write tests for health aggregation and display
