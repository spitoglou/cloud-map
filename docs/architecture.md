# Architecture

## Overview

Cloud Map is a CLI tool that connects to remote Linux servers via SSH to inspect Docker containers and systemd services, then presents health status in the terminal.

```
┌─────────────┐     SSH      ┌──────────────┐
│  cloud-map   │────────────▶│  Server A     │
│  (local CLI) │             │  - Docker     │
│              │────────────▶│  - systemd    │
│  ┌────────┐  │             └──────────────┘
│  │ Cache  │  │     SSH      ┌──────────────┐
│  │ (JSON) │  │────────────▶│  Server B     │
│  └────────┘  │             │  - Docker     │
└─────────────┘             └──────────────┘
```

## Components

### CLI (`cli.py`)
Entry point using Click. Provides commands: `ping`, `status`, `containers`, `services`. All commands accept `-i` / `--inventory` to specify the inventory file.

### Config (`config.py`)
Loads server inventory from a YAML file. Parses server definitions into `ServerConfig` dataclasses.

### SSH Manager (`ssh.py`)
Manages async SSH connections via `asyncssh`. Supports key-based and password-based authentication. Connections are reused within a session and handle timeouts gracefully.

### Docker Module (`docker.py`)
Lists and parses Docker containers by running `docker ps -a --format` over SSH. Extracts container ID, name, image, status, state, health, and ports.

### Resources Module (`resources.py`)
Collects system resource data (CPU, memory, disk) by running a compound shell command over SSH in a single round-trip. Parses output of `free -b`, `nproc`, `vmstat`, and `df`.

### Systemd Module (`systemd.py`)
Lists and parses systemd service status via SSH. Auto-discovers all services by running `systemctl list-units --type=service` when no explicit list is configured. Supports glob-based exclude patterns to filter out noisy internal services. Falls back to `systemctl show` for explicitly listed services.

### Collector (`collector.py`)
Orchestrates concurrent health data collection from all servers. Combines Docker and systemd results into unified `ServerStatus` objects.

### Models (`models.py`)
Dataclasses and enums: `HealthStatus` (healthy/unhealthy/degraded/unknown), `ServiceType` (docker/systemd), `ServerConfig`, `ContainerInfo`, `SystemdServiceInfo`, `ServiceInfo`, `ServerStatus`.

### Display (`display.py`)
Rich-based terminal output. Color-coded tables for status, containers, services, and fleet summary.

### PDF (`pdf.py`)
Generates printable PDF reports using `fpdf2`. Mirrors the terminal table output with formatted tables, color-coded health indicators, and fleet summaries. Each command has a corresponding PDF generator function.

### Cache (`cache.py`)
Persists last known state to a JSON file after each collection. Supports offline queries via `--cached` flag with staleness indicator.

## Data Flow

1. CLI loads inventory YAML → list of `ServerConfig`
2. Collector connects to each server via SSH concurrently
3. For each server: runs `docker ps`, `systemctl show`, and resource commands → parses into `ContainerInfo` / `SystemdServiceInfo` / `ResourceInfo`
4. Maps to unified `ServiceInfo` with `HealthStatus`, attaches `ResourceInfo` to `ServerStatus`
5. Aggregates into `ServerStatus` per server
6. Cache module saves results to JSON
7. Display module renders Rich tables to terminal
