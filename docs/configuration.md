# Configuration

## Inventory File

Cloud Map uses a YAML inventory file to define which servers to manage. By default it looks for `inventory.yaml` in the current directory.

### Format

```yaml
# Optional: path for the state cache file (default: .cloud-map-cache.json)
cache_path: .cloud-map-cache.json

servers:
  - name: web-prod-1              # Display name (defaults to hostname)
    hostname: 192.168.1.10        # Required: hostname or IP
    port: 22                      # SSH port (default: 22)
    username: deploy              # SSH username (default: root)
    key_path: ~/.ssh/id_ed25519   # Path to SSH private key
    docker_enabled: true          # Check Docker containers (default: true)
    systemd_services: []            # Empty = auto-discover all services
    systemd_exclude:                # Glob patterns to exclude from discovery
      - "systemd-*"
      - dbus

  - name: db-prod-1
    hostname: 192.168.1.20
    username: admin
    password: secret              # Password-based auth (key_path preferred)
    docker_enabled: false
    systemd_services:             # Explicit list = only monitor these
      - postgresql
      - pgbouncer
```

### Fields

| Field              | Required | Default                 | Description                              |
|--------------------|----------|-------------------------|------------------------------------------|
| `name`             | No       | Value of `hostname`     | Display name for the server              |
| `hostname`         | Yes      | —                       | Hostname or IP address                   |
| `port`             | No       | `22`                    | SSH port                                 |
| `username`         | No       | `root`                  | SSH username                             |
| `key_path`         | No       | —                       | Path to SSH private key                  |
| `password`         | No       | —                       | SSH password (use key_path when possible)|
| `docker_enabled`   | No       | `true`                  | Whether to check Docker containers       |
| `systemd_services` | No       | `[]`                    | Systemd units to monitor (empty = auto-discover) |
| `systemd_exclude`  | No       | `[]`                    | Glob patterns to exclude from auto-discovery |
| `cache_path`       | No       | `.cloud-map-cache.json` | Path for the local state cache file      |

### Authentication

Cloud Map supports two SSH authentication methods:

1. **Key-based** (recommended): Set `key_path` to your private key file
2. **Password-based**: Set `password` field (consider using environment variables or a secrets manager)

If neither `key_path` nor `password` is specified, Cloud Map falls back to SSH agent authentication.

### Systemd Service Discovery

By default (when `systemd_services` is empty), Cloud Map auto-discovers all running systemd services on the server. Use `systemd_exclude` to filter out noisy internal services using glob patterns:

```yaml
servers:
  - hostname: 10.0.0.1
    systemd_services: []          # Auto-discover all
    systemd_exclude:
      - "systemd-*"              # Exclude all systemd internal services
      - dbus                     # Exact match
      - "user@*"                 # Exclude user session services
```

If `systemd_services` is populated, only those specific services are checked and `systemd_exclude` is ignored.

### Example: Minimal Inventory

```yaml
servers:
  - hostname: 10.0.0.1
  - hostname: 10.0.0.2
    username: deploy
```
