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

## State Cache

Every live command (`status`, `containers`, `services`) automatically saves results to a local JSON cache file. Use `cloud-map status --cached` to view the last known state offline, including how long ago the data was collected.
