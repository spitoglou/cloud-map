"""YAML-based server inventory configuration loader."""

from __future__ import annotations

from pathlib import Path

import yaml

from cloud_map.models import InventoryConfig, ServerConfig


def load_inventory(path: str | Path) -> InventoryConfig:
    """Load server inventory from a YAML file.

    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the file is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Inventory file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "servers" not in data:
        raise ValueError(f"Invalid inventory file: {path} (must contain 'servers' key)")

    servers = []
    for entry in data["servers"]:
        if "hostname" not in entry:
            raise ValueError(f"Server entry missing 'hostname': {entry}")
        servers.append(
            ServerConfig(
                name=entry.get("name", entry["hostname"]),
                hostname=entry["hostname"],
                port=entry.get("port", 22),
                username=entry.get("username", "root"),
                key_path=entry.get("key_path"),
                password=entry.get("password"),
                docker_enabled=entry.get("docker_enabled", True),
                systemd_services=entry.get("systemd_services", []),
                systemd_exclude=entry.get("systemd_exclude", []),
            )
        )

    return InventoryConfig(
        servers=servers,
        cache_path=data.get("cache_path", ".cloud-map-cache.json"),
    )
