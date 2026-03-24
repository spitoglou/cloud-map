"""Tests for PDF report generation."""

import pytest

from cloud_map.models import HealthStatus, ServerStatus, ServiceInfo, ServiceType
from cloud_map.pdf import (
    generate_containers_pdf,
    generate_ping_pdf,
    generate_services_pdf,
    generate_status_pdf,
)


@pytest.fixture
def sample_statuses():
    return [
        ServerStatus(
            name="web-1",
            hostname="10.0.0.1",
            reachable=True,
            services=[
                ServiceInfo("nginx", ServiceType.DOCKER, HealthStatus.HEALTHY, "Up 2h"),
                ServiceInfo("sshd", ServiceType.SYSTEMD, HealthStatus.HEALTHY, "active (running)"),
            ],
        ),
        ServerStatus(
            name="db-1",
            hostname="10.0.0.2",
            reachable=False,
            error="Connection timed out",
        ),
        ServerStatus(
            name="worker-1",
            hostname="10.0.0.3",
            reachable=True,
            services=[],
        ),
    ]


@pytest.fixture
def ping_results():
    return [
        ("web-1", "10.0.0.1", True),
        ("db-1", "10.0.0.2", False),
    ]


def test_generate_status_pdf(tmp_path, sample_statuses):
    path = generate_status_pdf(sample_statuses, tmp_path / "status.pdf")
    assert path.exists()
    assert path.stat().st_size > 0
    content = path.read_bytes()
    assert content[:5] == b"%PDF-"


def test_generate_status_pdf_cached(tmp_path, sample_statuses):
    path = generate_status_pdf(
        sample_statuses, tmp_path / "cached.pdf", cached=True, cache_age="5 minutes ago"
    )
    assert path.exists()
    assert path.stat().st_size > 0


def test_generate_ping_pdf(tmp_path, ping_results):
    path = generate_ping_pdf(ping_results, tmp_path / "ping.pdf")
    assert path.exists()
    assert path.stat().st_size > 0
    content = path.read_bytes()
    assert content[:5] == b"%PDF-"


def test_generate_containers_pdf(tmp_path, sample_statuses):
    path = generate_containers_pdf(sample_statuses, tmp_path / "containers.pdf")
    assert path.exists()
    assert path.stat().st_size > 0


def test_generate_services_pdf(tmp_path, sample_statuses):
    path = generate_services_pdf(sample_statuses, tmp_path / "services.pdf")
    assert path.exists()
    assert path.stat().st_size > 0
