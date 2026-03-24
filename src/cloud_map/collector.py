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
from cloud_map.resources import collect_resources
from cloud_map.ssh import SSHManager
from cloud_map.systemd import SystemdNotAvailableError, list_services
from cloud_map.webserver import discover_domains


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
                meta = {"image": c.image, "state": c.state}
                if c.ports:
                    meta["ports"] = c.ports
                if c.health:
                    meta["health_check"] = c.health
                services.append(
                    ServiceInfo(
                        name=c.name,
                        service_type=ServiceType.DOCKER,
                        health=c.health_status,
                        detail=c.status,
                        metadata=meta,
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

    # Collect systemd services (auto-discovers if systemd_services is empty)
    try:
        systemd_svcs = await list_services(ssh, server)
        for s in systemd_svcs:
            meta: dict[str, str] = {
                "active_state": s.active_state,
                "sub_state": s.sub_state,
            }
            if s.description:
                meta["description"] = s.description
            services.append(
                ServiceInfo(
                    name=s.name,
                    service_type=ServiceType.SYSTEMD,
                    health=s.health_status,
                    detail=f"{s.active_state} ({s.sub_state})",
                    metadata=meta,
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

    # Collect system resources
    resources = await collect_resources(ssh, server)

    # Discover web server domains
    domains = await discover_domains(ssh, server)

    return ServerStatus(
        name=server.name,
        hostname=server.hostname,
        reachable=True,
        services=services,
        resources=resources,
        domains=domains,
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
