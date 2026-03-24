"""Tests for configuration loading."""

import pytest
import yaml

from cloud_map.config import load_inventory


@pytest.fixture
def inventory_file(tmp_path):
    """Create a temporary inventory file."""

    def _write(data):
        path = tmp_path / "inventory.yaml"
        path.write_text(yaml.dump(data))
        return path

    return _write


def test_load_valid_inventory(inventory_file):
    path = inventory_file(
        {
            "servers": [
                {
                    "name": "web-1",
                    "hostname": "10.0.0.1",
                    "port": 2222,
                    "username": "deploy",
                    "key_path": "~/.ssh/id_ed25519",
                    "docker_enabled": True,
                    "systemd_services": ["nginx", "redis"],
                }
            ],
            "cache_path": "/tmp/cache.json",
        }
    )
    inv = load_inventory(path)
    assert len(inv.servers) == 1
    s = inv.servers[0]
    assert s.name == "web-1"
    assert s.hostname == "10.0.0.1"
    assert s.port == 2222
    assert s.username == "deploy"
    assert s.key_path == "~/.ssh/id_ed25519"
    assert s.docker_enabled is True
    assert s.systemd_services == ["nginx", "redis"]
    assert inv.cache_path == "/tmp/cache.json"


def test_load_minimal_inventory(inventory_file):
    path = inventory_file({"servers": [{"hostname": "10.0.0.2"}]})
    inv = load_inventory(path)
    s = inv.servers[0]
    assert s.name == "10.0.0.2"
    assert s.port == 22
    assert s.username == "root"
    assert s.key_path is None
    assert s.password is None
    assert s.docker_enabled is True
    assert s.systemd_services == []


def test_load_password_auth(inventory_file):
    path = inventory_file({"servers": [{"hostname": "10.0.0.3", "password": "secret"}]})
    inv = load_inventory(path)
    assert inv.servers[0].password == "secret"


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_inventory("/nonexistent/path.yaml")


def test_missing_servers_key(inventory_file):
    path = inventory_file({"hosts": []})
    with pytest.raises(ValueError, match="must contain 'servers' key"):
        load_inventory(path)


def test_missing_hostname(inventory_file):
    path = inventory_file({"servers": [{"name": "no-host"}]})
    with pytest.raises(ValueError, match="missing 'hostname'"):
        load_inventory(path)
