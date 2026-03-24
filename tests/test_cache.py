"""Tests for state cache."""

from datetime import UTC, datetime, timedelta

import pytest

from cloud_map.cache import format_cache_age, load_cache, save_cache
from cloud_map.models import HealthStatus, ServerStatus, ServiceInfo, ServiceType


@pytest.fixture
def sample_statuses():
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
        ),
        ServerStatus(
            name="db-1",
            hostname="10.0.0.2",
            reachable=False,
            error="Connection timed out",
        ),
    ]


def test_save_and_load_cache(tmp_path, sample_statuses):
    cache_path = tmp_path / "cache.json"
    save_cache(sample_statuses, cache_path)
    loaded, collected_at = load_cache(cache_path)

    assert len(loaded) == 2
    assert loaded[0].name == "web-1"
    assert loaded[0].reachable is True
    assert len(loaded[0].services) == 2
    assert loaded[0].services[0].name == "nginx"
    assert loaded[0].services[0].health == HealthStatus.HEALTHY
    assert loaded[0].services[1].service_type == ServiceType.SYSTEMD
    assert loaded[1].reachable is False
    assert loaded[1].error == "Connection timed out"
    assert isinstance(collected_at, datetime)


def test_load_missing_cache(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_cache(tmp_path / "nonexistent.json")


class TestFormatCacheAge:
    def test_seconds(self):
        t = datetime.now(UTC) - timedelta(seconds=30)
        assert "30 seconds ago" == format_cache_age(t)

    def test_minutes(self):
        t = datetime.now(UTC) - timedelta(minutes=5)
        assert "5 minutes ago" == format_cache_age(t)

    def test_one_minute(self):
        t = datetime.now(UTC) - timedelta(minutes=1)
        assert "1 minute ago" == format_cache_age(t)

    def test_hours(self):
        t = datetime.now(UTC) - timedelta(hours=3)
        assert "3 hours ago" == format_cache_age(t)

    def test_days(self):
        t = datetime.now(UTC) - timedelta(days=2)
        assert "2 days ago" == format_cache_age(t)
