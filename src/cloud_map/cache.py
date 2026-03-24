"""State cache for offline status queries."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cloud_map.models import HealthStatus, ServerStatus, ServiceInfo, ServiceType


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
    return {
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
            }
            for svc in server.services
        ],
    }


def _deserialize_server(data: dict) -> ServerStatus:
    services = [
        ServiceInfo(
            name=s["name"],
            service_type=ServiceType(s["type"]),
            health=HealthStatus(s["health"]),
            detail=s.get("detail", ""),
        )
        for s in data.get("services", [])
    ]
    return ServerStatus(
        name=data["name"],
        hostname=data["hostname"],
        reachable=data["reachable"],
        error=data.get("error"),
        services=services,
    )
