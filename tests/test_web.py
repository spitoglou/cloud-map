"""Tests for the web dashboard."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from cloud_map.models import (
    CpuInfo,
    DomainInfo,
    HealthStatus,
    MemoryInfo,
    ResourceInfo,
    ServerStatus,
    ServiceInfo,
    ServiceType,
    WebServerType,
)
from cloud_map.web import app, configure

# Must install httpx for TestClient — fastapi bundles it as a test dep.
pytest.importorskip("httpx", reason="httpx required for FastAPI TestClient")


@pytest.fixture
def _sample_statuses():
    return [
        ServerStatus(
            name="web-1",
            hostname="10.0.0.1",
            reachable=True,
            services=[
                ServiceInfo("nginx", ServiceType.DOCKER, HealthStatus.HEALTHY, "Up 2h"),
                ServiceInfo(
                    "redis", ServiceType.SYSTEMD, HealthStatus.UNHEALTHY, "failed (failed)"
                ),
            ],
            resources=ResourceInfo(
                memory=MemoryInfo(total=8_000_000_000, used=4_000_000_000, available=4_000_000_000),
                cpu=CpuInfo(cores=4, usage_percent=35.0),
                disks=[],
            ),
            domains=[
                DomainInfo("example.com", WebServerType.NGINX, "/etc/nginx/conf.d/app.conf"),
            ],
        ),
        ServerStatus(
            name="db-1",
            hostname="10.0.0.2",
            reachable=False,
            error="Connection timed out",
        ),
    ]


@pytest.fixture
def client(_sample_statuses):
    from cloud_map.models import InventoryConfig, ServerConfig

    inventory = InventoryConfig(
        servers=[ServerConfig(name="web-1", hostname="10.0.0.1")],
        cache_path="test-cache.json",
    )
    configure(inventory, refresh=15)

    with patch("cloud_map.web.collect_all", new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = _sample_statuses
        with patch("cloud_map.web.save_cache"):
            with patch("cloud_map.web.load_cache", side_effect=FileNotFoundError):
                # Reset last_collected so it always triggers fresh collection.
                import cloud_map.web as web_mod

                web_mod._last_collected = 0.0
                yield TestClient(app)


def test_dashboard_returns_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Cloud Map" in resp.text


def test_dashboard_contains_server_names(client):
    resp = client.get("/")
    assert "web-1" in resp.text
    assert "db-1" in resp.text


def test_api_status_returns_json(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_api_status_server_fields(client):
    resp = client.get("/api/status")
    data = resp.json()
    web = next(s for s in data if s["name"] == "web-1")
    assert web["reachable"] is True
    assert web["hostname"] == "10.0.0.1"
    assert len(web["services"]) == 2
    assert web["resources"]["cpu"]["cores"] == 4

    db = next(s for s in data if s["name"] == "db-1")
    assert db["reachable"] is False
    assert db["error"] == "Connection timed out"


def test_api_status_includes_domains(client):
    resp = client.get("/api/status")
    data = resp.json()
    web = next(s for s in data if s["name"] == "web-1")
    assert len(web["domains"]) == 1
    assert web["domains"][0]["domain"] == "example.com"
    assert web["domains"][0]["web_server_type"] == "nginx"


def test_dashboard_default_refresh(client):
    resp = client.get("/")
    # The template should embed the configured default refresh value.
    assert "15" in resp.text
