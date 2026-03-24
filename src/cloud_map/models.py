"""Data models for Cloud Map."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime


class HealthStatus(enum.Enum):
    """Health status of a service."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceType(enum.Enum):
    """Type of managed service."""

    DOCKER = "docker"
    SYSTEMD = "systemd"


@dataclass
class ServerConfig:
    """Configuration for a single server."""

    name: str
    hostname: str
    port: int = 22
    username: str = "root"
    key_path: str | None = None
    password: str | None = None
    docker_enabled: bool = True
    systemd_services: list[str] = field(default_factory=list)
    systemd_exclude: list[str] = field(default_factory=list)


@dataclass
class InventoryConfig:
    """Top-level inventory configuration."""

    servers: list[ServerConfig]
    cache_path: str = ".cloud-map-cache.json"


@dataclass
class ContainerInfo:
    """Docker container information."""

    container_id: str
    name: str
    image: str
    status: str
    state: str
    health: str | None = None
    ports: str = ""

    @property
    def health_status(self) -> HealthStatus:
        if self.health == "healthy":
            return HealthStatus.HEALTHY
        if self.health in ("unhealthy", "no healthcheck"):
            if self.state == "running" and self.health == "no healthcheck":
                return HealthStatus.HEALTHY
            return HealthStatus.UNHEALTHY
        if self.state == "running":
            return HealthStatus.HEALTHY
        if self.state in ("restarting", "created"):
            return HealthStatus.DEGRADED
        return HealthStatus.UNHEALTHY


@dataclass
class SystemdServiceInfo:
    """Systemd service information."""

    name: str
    active_state: str
    sub_state: str
    description: str = ""

    @property
    def health_status(self) -> HealthStatus:
        if self.active_state == "active" and self.sub_state == "running":
            return HealthStatus.HEALTHY
        if self.active_state == "failed":
            return HealthStatus.UNHEALTHY
        if self.active_state in ("activating", "deactivating", "reloading"):
            return HealthStatus.DEGRADED
        if self.active_state == "inactive":
            return HealthStatus.UNHEALTHY
        return HealthStatus.UNKNOWN


@dataclass
class ServiceInfo:
    """Unified service info combining Docker and systemd."""

    name: str
    service_type: ServiceType
    health: HealthStatus
    detail: str = ""


@dataclass
class ServerStatus:
    """Status of a single server."""

    name: str
    hostname: str
    reachable: bool
    services: list[ServiceInfo] = field(default_factory=list)
    error: str | None = None
    collected_at: datetime | None = None

    @property
    def summary(self) -> dict[HealthStatus, int]:
        counts: dict[HealthStatus, int] = {s: 0 for s in HealthStatus}
        for svc in self.services:
            counts[svc.health] += 1
        return counts
