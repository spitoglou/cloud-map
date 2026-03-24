# Capabilities

## CLI Commands

### `cloud-map ping`
Test SSH connectivity to all configured servers.

```bash
cloud-map ping
cloud-map -i custom-inventory.yaml ping
```

Displays a table with server name, hostname, and reachable/unreachable status.

### `cloud-map status`
Display health status of all servers and services.

```bash
cloud-map status           # Live collection from all servers
cloud-map status --cached  # Show last known state (no SSH connections)
```

Options:
- `--cached` — Display last known state from cache without connecting to servers. Shows cache age.

Displays a color-coded table:
- Green (●) = healthy
- Red (●) = unhealthy
- Yellow (●) = degraded
- Gray (○) = unknown

Includes a fleet-level summary with total counts.

### `cloud-map containers`
List Docker containers across all servers.

```bash
cloud-map containers
```

Displays container name, status, and health for each reachable server.

### `cloud-map services`
List systemd services across all servers.

```bash
cloud-map services
```

Displays service name, active state, sub-state, and health for each reachable server. Auto-discovers all services unless `systemd_services` is explicitly set. Use `systemd_exclude` to filter out unwanted services.

### `cloud-map web`
Start a web monitoring dashboard. Launches a FastAPI server with a Jinja2-rendered dark-themed UI showing server health, containers, services, and resource usage.

```bash
cloud-map web                              # Start on 0.0.0.0:8000
cloud-map web --host 127.0.0.1 --port 9090 # Custom bind address
cloud-map web --refresh 60                 # Default 60s auto-refresh
```

Options:
- `--host` — Address to bind to (default: `0.0.0.0`)
- `--port` — Port to bind to (default: `8000`)
- `--refresh` — Default auto-refresh interval in seconds (default: `30`)

The dashboard has four tabs: Overview, Containers, Services, and Resources. The refresh interval can be changed from the UI at any time via a dropdown. Data is cached for 30 seconds to avoid redundant SSH connections on rapid refreshes.

### `cloud-map domains`
Discover and display web server domains configured in nginx and Apache httpd across all servers. Auto-detects installed web servers by probing standard config directories.

```bash
cloud-map domains
cloud-map domains --pdf domains.pdf
```

Extracts `server_name` (nginx) and `ServerName`/`ServerAlias` (Apache) directives. Checks `/etc/nginx/`, `/etc/httpd/`, and `/etc/apache2/` by default. Override paths or disable per-server via the `webservers` inventory field.

## Global Options

### `-i` / `--inventory`
Path to the inventory YAML file. Defaults to `inventory.yaml`. Can also be set via `CLOUD_MAP_INVENTORY` environment variable.

```bash
cloud-map -i /path/to/servers.yaml status
CLOUD_MAP_INVENTORY=/path/to/servers.yaml cloud-map status
```

## Health Model

| Status    | Meaning                                         |
|-----------|--------------------------------------------------|
| healthy   | Service running, health check passing            |
| unhealthy | Service failed, exited, or health check failing  |
| degraded  | Service restarting, activating, or transitioning |
| unknown   | Server unreachable or service state unclear      |

### `cloud-map resources`
Display system resource usage across all servers.

```bash
cloud-map resources
cloud-map resources --pdf resources.pdf
```

Displays CPU cores, CPU usage percentage, memory (used/total/available), and disk partitions (mount, used/total) for each reachable server. Values are color-coded by usage threshold: green (<70%), yellow (70-90%), red (>90%).

## PDF Export

All commands support the `--pdf <path>` option to generate a printable PDF report. The PDF includes the same data as the terminal output with formatted tables, color-coded health indicators, and a fleet summary (for the `status` command).

```bash
cloud-map status --pdf report.pdf
cloud-map containers --pdf containers.pdf
cloud-map services --pdf services.pdf
cloud-map ping --pdf connectivity.pdf
cloud-map status --cached --pdf cached-report.pdf
```

The PDF is generated alongside the normal terminal output — both are shown.

## State Cache

Every live command (`status`, `containers`, `services`) automatically saves results to a local JSON cache file. Use `cloud-map status --cached` to view the last known state offline, including how long ago the data was collected.
