# Cloud Map

Cloud server administration tool that connects to remote Linux servers via SSH to manage Docker containers and systemd services, with color-coded terminal visualization of service health.

## Features

- SSH connectivity testing across your server fleet
- System resource monitoring (CPU, memory, disk usage)
- Docker container listing and health status
- Systemd service monitoring
- Color-coded Rich terminal tables with fleet-level health summary
- Offline cached status — view last known state without connecting
- PDF export for all commands via `--pdf`
- Web server domain discovery (nginx and Apache httpd auto-detection)
- Web monitoring dashboard with auto-refresh (FastAPI + Jinja2)
- YAML-based server inventory
- Key-based and password-based SSH authentication

## Requirements

- Python 3.13+
- [UV](https://docs.astral.sh/uv/) package manager

## Installation

```bash
git clone <repo-url>
cd cloud-map
uv sync
```

## Quick Start

1. Copy the example inventory and customize it:

```bash
cp inventory.example.yaml inventory.yaml
```

2. Edit `inventory.yaml` with your servers:

```yaml
servers:
  - name: web-prod-1
    hostname: 192.168.1.10
    username: deploy
    key_path: ~/.ssh/id_ed25519
    docker_enabled: true
    systemd_services:
      - nginx
      - redis
```

3. Test connectivity:

```bash
uv run cloud-map ping
```

4. View health status:

```bash
uv run cloud-map status
```

## Commands

### `cloud-map ping`

Test SSH connectivity to all configured servers.

```bash
cloud-map ping
cloud-map -i custom-inventory.yaml ping
```

### `cloud-map status`

Display health status of all servers and services in a color-coded table.

```bash
cloud-map status           # Live collection from all servers
cloud-map status --cached  # Show last known state (no SSH connections)
```

The `--cached` flag displays the last collected state offline with a staleness indicator (e.g., "Last updated: 2 hours ago").

Health indicators:
- Green = healthy
- Red = unhealthy
- Yellow = degraded
- Gray = unknown

Includes a fleet-level summary with total counts per status.

### `cloud-map containers`

List Docker containers across all servers with name, status, and health.

```bash
cloud-map containers
```

### `cloud-map services`

List systemd services across all servers with active state and health. Auto-discovers all services by default; use `systemd_services` for an explicit list or `systemd_exclude` to filter out noise.

```bash
cloud-map services
```

### `cloud-map resources`

Display system resource usage (CPU cores/usage, memory, disk space) across all servers.

```bash
cloud-map resources
cloud-map resources --pdf resources.pdf
```

Color-coded thresholds: green (<70%), yellow (70-90%), red (>90%).

### `cloud-map domains`

Discover and display web server domains (nginx `server_name`, Apache `ServerName`/`ServerAlias`) across all servers. Auto-detects nginx and Apache httpd by probing standard config directories — no inventory changes needed.

```bash
cloud-map domains
cloud-map domains --pdf domains.pdf
```

To override config paths or disable auto-detection for a server, add a `webservers` field to its inventory entry:

```yaml
servers:
  - name: web-prod-1
    hostname: 10.0.0.1
    webservers:
      - type: nginx
        config_path: /opt/nginx/conf  # custom path
      - type: httpd

  - name: db-1
    hostname: 10.0.0.2
    webservers: false  # disable auto-detection
```

### `cloud-map web`

Start a web monitoring dashboard in your browser. Shows the same data as the CLI commands in a live-updating dark-themed UI with tabs for overview, containers, services, resources, and domains.

```bash
cloud-map web                              # Start on 0.0.0.0:8000
cloud-map web --host 127.0.0.1 --port 9090 # Custom bind address
cloud-map web --refresh 60                 # Default 60s auto-refresh interval
```

| Option | Default | Description |
|---|---|---|
| `--host` | `0.0.0.0` | Address to bind the web server to |
| `--port` | `8000` | Port to bind the web server to |
| `--refresh` | `30` | Default auto-refresh interval in seconds |

The refresh interval can also be changed from the dashboard UI at any time.

### Global Options

| Option | Env Variable | Default | Description |
|---|---|---|---|
| `-i` / `--inventory` | `CLOUD_MAP_INVENTORY` | `inventory.yaml` | Path to inventory YAML file |
| `--pdf <path>` | — | — | Export output to a PDF file |

All commands support `--pdf` to generate a printable PDF report alongside the terminal output:

```bash
cloud-map status --pdf report.pdf
cloud-map containers --pdf containers.pdf
cloud-map services --pdf services.pdf
cloud-map ping --pdf connectivity.pdf
cloud-map resources --pdf resources.pdf
cloud-map status --cached --pdf cached-report.pdf
```

## Configuration

### Inventory File

Cloud Map uses a YAML inventory file to define which servers to manage. See `inventory.example.yaml` for a complete example.

```yaml
cache_path: .cloud-map-cache.json   # Optional, default shown

servers:
  - name: web-prod-1               # Display name (defaults to hostname)
    hostname: 192.168.1.10         # Required
    port: 22                       # Default: 22
    username: deploy               # Default: root
    key_path: ~/.ssh/id_ed25519    # SSH private key path
    password: null                 # Or use password-based auth
    docker_enabled: true           # Check Docker containers (default: true)
    systemd_services: []           # Empty = auto-discover all (default)
    systemd_exclude:               # Glob patterns to exclude from discovery
      - "systemd-*"
      - dbus
      - nginx
      - postgresql
```

### Server Fields

| Field | Required | Default | Description |
|---|---|---|---|
| `name` | No | hostname | Display name |
| `hostname` | **Yes** | — | Hostname or IP address |
| `port` | No | `22` | SSH port |
| `username` | No | `root` | SSH username |
| `key_path` | No | — | Path to SSH private key |
| `password` | No | — | SSH password |
| `docker_enabled` | No | `true` | Whether to check Docker containers |
| `systemd_services` | No | `[]` | Systemd units to monitor (empty = auto-discover) |
| `systemd_exclude` | No | `[]` | Glob patterns to exclude from auto-discovery |
| `cache_path` | No | `.cloud-map-cache.json` | State cache file path (top-level) |

### Authentication

Three methods, tried in order of preference:

1. **Key-based** — set `key_path` to your private key
2. **Password-based** — set `password` (consider a secrets manager)
3. **SSH agent** — if neither key nor password is set, falls back to the SSH agent

## State Cache

Every live command (`status`, `containers`, `services`) automatically persists results to a local JSON cache file. Use `cloud-map status --cached` to view the last known state without connecting to any server. The cache display includes how long ago the data was collected.

## Development

```bash
# Install with dev dependencies
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Install pre-commit hooks
uv run pre-commit install
```

### Pre-commit Hooks

The project uses pre-commit hooks that enforce:

- **Ruff** linting and formatting
- **Documentation updates** — commits that modify `src/` must also include changes to at least one file under `docs/`. This also applies to `README.md` changes when appropriate.

### Project Structure

```
src/cloud_map/
  cli.py          CLI entry point (Click)
  web.py          Web dashboard (FastAPI + Jinja2)
  templates/      Jinja2 HTML templates
  webserver.py    Web server domain discovery (nginx, Apache)
  pdf.py          PDF report generation (fpdf2)
  resources.py    System resource collection (CPU, memory, disk)
  config.py       YAML inventory loader
  ssh.py          Async SSH connection manager
  docker.py       Docker container listing/parsing
  systemd.py      Systemd service listing/parsing
  collector.py    Concurrent health data collection
  cache.py        JSON state cache with staleness tracking
  display.py      Rich terminal visualization
  models.py       Domain dataclasses and enums
docs/             Architecture, capabilities, and configuration docs
tests/            Unit tests
```

## Documentation

Detailed documentation lives in the `docs/` folder:

- [`docs/architecture.md`](docs/architecture.md) — system design, components, data flow
- [`docs/capabilities.md`](docs/capabilities.md) — CLI commands, flags, usage examples
- [`docs/configuration.md`](docs/configuration.md) — inventory file format and options
