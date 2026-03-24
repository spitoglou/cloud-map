"""Health data collector - orchestrates gathering status from all servers."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from cloud_map.docker import DockerNotAvailableError, list_containers
from cloud_map.models import (
    HealthStatus,
    InventoryConfig,
    ServerConfig,
    ServerStatus,
    ServiceInfo,
    ServiceType,
)
from cloud_map.ssh import SSHManager
from cloud_map.systemd import SystemdNotAvailableError, list_services


async def collect_server_status(ssh: SSHManager, server: ServerConfig) -> ServerStatus:
    """Collect full status for a single server."""
    services: list[ServiceInfo] = []

    # Check reachability
    reachable = await ssh.check_reachable(server)
    if not reachable:
        return ServerStatus(
            name=server.name,
            hostname=server.hostname,
            reachable=False,
            error="Server unreachable",
            collected_at=datetime.now(UTC),
        )

    # Collect Docker containers
    if server.docker_enabled:
        try:
            containers = await list_containers(ssh, server)
            for c in containers:
                services.append(
                    ServiceInfo(
                        name=c.name,
                        service_type=ServiceType.DOCKER,
                        health=c.health_status,
                        detail=c.status,
                    )
                )
        except DockerNotAvailableError:
            services.append(
                ServiceInfo(
                    name="docker",
                    service_type=ServiceType.DOCKER,
                    health=HealthStatus.UNKNOWN,
                    detail="Docker not available",
                )
            )

    # Collect systemd services
    if server.systemd_services:
        try:
            systemd_svcs = await list_services(ssh, server)
            for s in systemd_svcs:
                services.append(
                    ServiceInfo(
                        name=s.name,
                        service_type=ServiceType.SYSTEMD,
                        health=s.health_status,
                        detail=f"{s.active_state} ({s.sub_state})",
                    )
                )
        except SystemdNotAvailableError:
            services.append(
                ServiceInfo(
                    name="systemd",
                    service_type=ServiceType.SYSTEMD,
                    health=HealthStatus.UNKNOWN,
                    detail="systemd not available",
                )
            )

    return ServerStatus(
        name=server.name,
        hostname=server.hostname,
        reachable=True,
        services=services,
        collected_at=datetime.now(UTC),
    )


async def collect_all(inventory: InventoryConfig) -> list[ServerStatus]:
    """Collect status from all servers concurrently."""
    ssh = SSHManager()
    try:
        tasks = [collect_server_status(ssh, server) for server in inventory.servers]
        return await asyncio.gather(*tasks)
    finally:
        await ssh.close_all()
