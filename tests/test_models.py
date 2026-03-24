"""Tests for data models."""

from cloud_map.models import (
    ContainerInfo,
    HealthStatus,
    ServerStatus,
    ServiceInfo,
    ServiceType,
    SystemdServiceInfo,
)


class TestContainerHealthStatus:
    def test_running_healthy(self):
        c = ContainerInfo("id", "web", "nginx", "Up 2h (healthy)", "running", "healthy")
        assert c.health_status == HealthStatus.HEALTHY

    def test_running_no_healthcheck(self):
        c = ContainerInfo("id", "web", "nginx", "Up 2h", "running", "no healthcheck")
        assert c.health_status == HealthStatus.HEALTHY

    def test_running_unhealthy(self):
        c = ContainerInfo("id", "web", "nginx", "Up 2h (unhealthy)", "running", "unhealthy")
        assert c.health_status == HealthStatus.UNHEALTHY

    def test_exited(self):
        c = ContainerInfo("id", "web", "nginx", "Exited (1)", "exited", None)
        assert c.health_status == HealthStatus.UNHEALTHY

    def test_restarting(self):
        c = ContainerInfo("id", "web", "nginx", "Restarting", "restarting", None)
        assert c.health_status == HealthStatus.DEGRADED

    def test_created(self):
        c = ContainerInfo("id", "web", "nginx", "Created", "created", None)
        assert c.health_status == HealthStatus.DEGRADED


class TestSystemdHealthStatus:
    def test_active_running(self):
        s = SystemdServiceInfo("nginx", "active", "running")
        assert s.health_status == HealthStatus.HEALTHY

    def test_failed(self):
        s = SystemdServiceInfo("nginx", "failed", "failed")
        assert s.health_status == HealthStatus.UNHEALTHY

    def test_inactive(self):
        s = SystemdServiceInfo("nginx", "inactive", "dead")
        assert s.health_status == HealthStatus.UNHEALTHY

    def test_activating(self):
        s = SystemdServiceInfo("nginx", "activating", "start")
        assert s.health_status == HealthStatus.DEGRADED

    def test_unknown_state(self):
        s = SystemdServiceInfo("nginx", "maintenance", "unknown")
        assert s.health_status == HealthStatus.UNKNOWN


class TestServerStatus:
    def test_summary(self):
        server = ServerStatus(
            name="test",
            hostname="10.0.0.1",
            reachable=True,
            services=[
                ServiceInfo("a", ServiceType.DOCKER, HealthStatus.HEALTHY),
                ServiceInfo("b", ServiceType.DOCKER, HealthStatus.HEALTHY),
                ServiceInfo("c", ServiceType.SYSTEMD, HealthStatus.UNHEALTHY),
                ServiceInfo("d", ServiceType.SYSTEMD, HealthStatus.DEGRADED),
            ],
        )
        summary = server.summary
        assert summary[HealthStatus.HEALTHY] == 2
        assert summary[HealthStatus.UNHEALTHY] == 1
        assert summary[HealthStatus.DEGRADED] == 1
        assert summary[HealthStatus.UNKNOWN] == 0
