"""On-demand log retrieval for Docker containers and systemd services."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cloud_map.models import ServerConfig
    from cloud_map.ssh import SSHManager

MAX_LINES = 10_000
DEFAULT_LINES = 100


async def fetch_docker_logs(
    ssh: SSHManager,
    server: ServerConfig,
    container: str,
    lines: int = DEFAULT_LINES,
) -> str:
    """Fetch recent log output from a Docker container."""
    lines = min(lines, MAX_LINES)
    cmd = f"docker logs --tail {lines} {_shell_quote(container)} 2>&1"
    return await ssh.run_command(server, cmd)


async def fetch_systemd_logs(
    ssh: SSHManager,
    server: ServerConfig,
    service: str,
    lines: int = DEFAULT_LINES,
) -> str:
    """Fetch recent journal output for a systemd service."""
    lines = min(lines, MAX_LINES)
    cmd = f"journalctl -u {_shell_quote(service)} -n {lines} --no-pager 2>&1"
    return await ssh.run_command(server, cmd)


async def fetch_logs(
    ssh: SSHManager,
    server: ServerConfig,
    service_name: str,
    service_type: str,
    lines: int = DEFAULT_LINES,
) -> str:
    """Fetch logs for a service, dispatching by type."""
    if service_type == "docker":
        return await fetch_docker_logs(ssh, server, service_name, lines)
    return await fetch_systemd_logs(ssh, server, service_name, lines)


def _shell_quote(s: str) -> str:
    """Simple shell quoting to prevent injection."""
    return "'" + s.replace("'", "'\\''") + "'"
