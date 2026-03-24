"""State cache for offline status queries."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cloud_map.models import (
    CpuInfo,
    DiskInfo,
    DomainInfo,
    HealthStatus,
    MemoryInfo,
    ResourceInfo,
    ServerStatus,
    ServiceInfo,
    ServiceType,
    WebServerType,
)


def save_cache(statuses: list[ServerStatus], cache_path: str | Path) -> None:
    """Persist server statuses to a JSON cache file."""
    path = Path(cache_path)
    data = {
        "collected_at": datetime.now(UTC).isoformat(),
        "servers": [_serialize_server(s) for s in statuses],
    }
    path.write_text(json.dumps(data, indent=2))


def load_cache(cache_path: str | Path) -> tuple[list[ServerStatus], datetime]:
    """Load cached server statuses.

    Returns (statuses, collected_at).
    Raises FileNotFoundError if no cache exists.
    """
    path = Path(cache_path)
    if not path.exists():
        raise FileNotFoundError(f"No cached data found at {path}")

    data = json.loads(path.read_text())
    collected_at = datetime.fromisoformat(data["collected_at"])
    servers = [_deserialize_server(s) for s in data["servers"]]
    return servers, collected_at


def format_cache_age(collected_at: datetime) -> str:
    """Format the age of cached data as a human-readable string."""
    now = datetime.now(UTC)
    if collected_at.tzinfo is None:
        collected_at = collected_at.replace(tzinfo=UTC)
    delta = now - collected_at
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds} seconds ago"
    if total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    if total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = total_seconds // 86400
    return f"{days} day{'s' if days != 1 else ''} ago"


def _serialize_server(server: ServerStatus) -> dict:
    result = {
        "name": server.name,
        "hostname": server.hostname,
        "reachable": server.reachable,
        "error": server.error,
        "services": [
            {
                "name": svc.name,
                "type": svc.service_type.value,
                "health": svc.health.value,
                "detail": svc.detail,
                "metadata": svc.metadata,
            }
            for svc in server.services
        ],
    }
    if server.resources:
        r = server.resources
        result["resources"] = {
            "memory": {
                "total": r.memory.total,
                "used": r.memory.used,
                "available": r.memory.available,
            }
            if r.memory
            else None,
            "cpu": {
                "cores": r.cpu.cores,
                "usage_percent": r.cpu.usage_percent,
            }
            if r.cpu
            else None,
            "disks": [
                {
                    "mount": d.mount,
                    "total": d.total,
                    "used": d.used,
                    "available": d.available,
                }
                for d in r.disks
            ],
        }
    if server.domains:
        result["domains"] = [
            {
                "domain": d.domain,
                "web_server_type": d.web_server_type.value,
                "config_file": d.config_file,
            }
            for d in server.domains
        ]
    return result


def _deserialize_server(data: dict) -> ServerStatus:
    services = [
        ServiceInfo(
            name=s["name"],
            service_type=ServiceType(s["type"]),
            health=HealthStatus(s["health"]),
            detail=s.get("detail", ""),
            metadata=s.get("metadata", {}),
        )
        for s in data.get("services", [])
    ]
    resources = None
    if "resources" in data and data["resources"]:
        rd = data["resources"]
        memory = None
        if rd.get("memory"):
            m = rd["memory"]
            memory = MemoryInfo(total=m["total"], used=m["used"], available=m["available"])
        cpu = None
        if rd.get("cpu"):
            c = rd["cpu"]
            cpu = CpuInfo(cores=c["cores"], usage_percent=c["usage_percent"])
        disks = [
            DiskInfo(mount=d["mount"], total=d["total"], used=d["used"], available=d["available"])
            for d in rd.get("disks", [])
        ]
        resources = ResourceInfo(memory=memory, cpu=cpu, disks=disks)

    domains = [
        DomainInfo(
            domain=d["domain"],
            web_server_type=WebServerType(d["web_server_type"]),
            config_file=d.get("config_file", ""),
        )
        for d in data.get("domains", [])
    ]

    return ServerStatus(
        name=data["name"],
        hostname=data["hostname"],
        reachable=data["reachable"],
        error=data.get("error"),
        services=services,
        resources=resources,
        domains=domains,
    )
