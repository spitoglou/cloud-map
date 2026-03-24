"""Docker container management via SSH."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from cloud_map.models import ContainerInfo

if TYPE_CHECKING:
    from cloud_map.models import ServerConfig
    from cloud_map.ssh import SSHManager

# Docker format template for structured output
_DOCKER_FORMAT = (
    '{"ID":"{{.ID}}","Name":"{{.Names}}","Image":"{{.Image}}",'
    '"Status":"{{.Status}}","State":"{{.State}}","Ports":"{{.Ports}}"}'
)


async def list_containers(ssh: SSHManager, server: ServerConfig) -> list[ContainerInfo]:
    """List all Docker containers on a remote server."""
    try:
        output = await ssh.run_command(server, f"docker ps -a --format '{_DOCKER_FORMAT}'")
    except RuntimeError as e:
        if "not found" in str(e).lower() or "not installed" in str(e).lower():
            raise DockerNotAvailableError(f"Docker not available on {server.name}") from e
        raise

    containers = []
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        health = _parse_health(data["Status"])
        containers.append(
            ContainerInfo(
                container_id=data["ID"],
                name=data["Name"],
                image=data["Image"],
                status=data["Status"],
                state=data["State"].lower(),
                health=health,
                ports=data["Ports"],
            )
        )
    return containers


def _parse_health(status: str) -> str | None:
    """Extract health status from Docker status string."""
    status_lower = status.lower()
    if "(healthy)" in status_lower:
        return "healthy"
    if "(unhealthy)" in status_lower:
        return "unhealthy"
    if "(health: starting)" in status_lower:
        return "starting"
    return "no healthcheck"


class DockerNotAvailableError(Exception):
    """Raised when Docker is not available on a server."""
