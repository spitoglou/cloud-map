"""Web dashboard for Cloud Map — FastAPI + Jinja2."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from cloud_map.cache import load_cache, save_cache
from cloud_map.collector import collect_all
from cloud_map.logs import MAX_LINES, fetch_logs
from cloud_map.models import InventoryConfig
from cloud_map.ssh import SSHManager

TEMPLATE_DIR = Path(__file__).parent / "templates"

app = FastAPI(title="Cloud Map Dashboard")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Set at startup by the CLI command.
_inventory: InventoryConfig | None = None
_default_refresh: int = 30
_cache_ttl: int = 30

# Simple in-memory lock to prevent concurrent collections.
_collection_lock = asyncio.Lock()
_last_collected: float = 0.0


def configure(inventory: InventoryConfig, refresh: int = 30, cache_ttl: int = 30) -> None:
    """Configure the web app before starting uvicorn."""
    global _inventory, _default_refresh, _cache_ttl  # noqa: PLW0603
    _inventory = inventory
    _default_refresh = refresh
    _cache_ttl = cache_ttl


async def _get_statuses() -> list[dict]:
    """Return server statuses, using cache when fresh enough."""
    global _last_collected  # noqa: PLW0603
    assert _inventory is not None

    now = time.monotonic()
    if now - _last_collected < _cache_ttl:
        try:
            statuses, _ = load_cache(_inventory.cache_path)
            return _serialize_statuses(statuses)
        except FileNotFoundError:
            pass

    async with _collection_lock:
        # Re-check after acquiring lock (another request may have collected).
        if time.monotonic() - _last_collected < _cache_ttl:
            try:
                statuses, _ = load_cache(_inventory.cache_path)
                return _serialize_statuses(statuses)
            except FileNotFoundError:
                pass

        statuses = await collect_all(_inventory)
        save_cache(list(statuses), _inventory.cache_path)
        _last_collected = time.monotonic()
        return _serialize_statuses(list(statuses))


def _serialize_statuses(statuses) -> list[dict]:
    """Convert ServerStatus objects to JSON-friendly dicts."""
    results = []
    for s in statuses:
        server: dict = {
            "name": s.name,
            "hostname": s.hostname,
            "reachable": s.reachable,
            "error": s.error,
            "services": [
                {
                    "name": svc.name,
                    "type": svc.service_type.value,
                    "health": svc.health.value,
                    "detail": svc.detail,
                    "metadata": svc.metadata,
                }
                for svc in s.services
            ],
            "resources": None,
            "domains": [
                {
                    "domain": d.domain,
                    "web_server_type": d.web_server_type.value,
                    "config_file": d.config_file,
                }
                for d in s.domains
            ],
        }
        if s.resources:
            r = s.resources
            server["resources"] = {
                "memory": {
                    "total": r.memory.total,
                    "used": r.memory.used,
                    "available": r.memory.available,
                    "used_percent": round(r.memory.used_percent, 1),
                }
                if r.memory
                else None,
                "cpu": {
                    "cores": r.cpu.cores,
                    "usage_percent": round(r.cpu.usage_percent, 1),
                }
                if r.cpu
                else None,
                "disks": [
                    {
                        "mount": d.mount,
                        "total": d.total,
                        "used": d.used,
                        "available": d.available,
                        "used_percent": round(d.used_percent, 1),
                    }
                    for d in r.disks
                ],
            }
        results.append(server)
    return results


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the main dashboard page."""
    statuses = await _get_statuses()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"servers": statuses, "default_refresh": _default_refresh},
    )


@app.get("/api/status")
async def api_status() -> list[dict]:
    """Return current server statuses as JSON."""
    return await _get_statuses()


@app.get("/api/logs/{server}/{service}", response_class=PlainTextResponse)
async def api_logs(
    server: str,
    service: str,
    lines: int = Query(default=100, ge=1, le=MAX_LINES),
) -> PlainTextResponse:
    """Fetch recent logs for a container or service."""
    assert _inventory is not None

    server_cfg = next((s for s in _inventory.servers if s.name == server), None)
    if not server_cfg:
        return PlainTextResponse(f"Server '{server}' not found.", status_code=404)

    # Determine service type from cached status data.
    svc_type = _resolve_service_type(server, service)

    ssh = SSHManager()
    try:
        output = await fetch_logs(ssh, server_cfg, service, svc_type, lines)
        return PlainTextResponse(output)
    except RuntimeError as e:
        return PlainTextResponse(str(e), status_code=500)
    finally:
        await ssh.close_all()


def _resolve_service_type(server_name: str, service_name: str) -> str:
    """Look up service type from cache."""
    assert _inventory is not None
    try:
        statuses, _ = load_cache(_inventory.cache_path)
        for s in statuses:
            if s.name == server_name:
                for svc in s.services:
                    if svc.name == service_name:
                        return svc.service_type.value
    except (FileNotFoundError, KeyError):
        pass
    return "docker"
