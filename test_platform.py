import json
import socket

import platform_cli as platform


def test_find_free_port_returns_an_actually_free_port():
    port = platform.find_free_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # If it's truly free, we should be able to bind to it ourselves.
        s.bind(("127.0.0.1", port))


def test_registry_round_trip(tmp_path, monkeypatch):
    fake_registry = tmp_path / "registry.json"
    monkeypatch.setattr(platform, "REGISTRY_PATH", fake_registry)

    assert platform.load_registry() == {}

    data = {"hello": {"image": "platform/hello", "host_port": 8000}}
    platform.save_registry(data)

    assert json.loads(fake_registry.read_text()) == data
    assert platform.load_registry() == data
