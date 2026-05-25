"""Unit tests for camera stream reachability probe."""

from __future__ import annotations

from unittest.mock import patch

from app.services.camera_probe import (
    probe_many_statuses,
    probe_status,
    probe_stream_reachable,
    resolve_stream_host_port,
)


def test_resolve_stream_host_port_defaults() -> None:
    assert resolve_stream_host_port("http://cam.local/live") == ("cam.local", 80)
    assert resolve_stream_host_port("https://cam.local:8443/v") == (
        "cam.local",
        8443,
    )
    assert resolve_stream_host_port("rtsp://10.0.0.5/stream") == ("10.0.0.5", 554)


def test_resolve_stream_host_port_invalid() -> None:
    assert resolve_stream_host_port("ftp://example.com/v") is None
    assert resolve_stream_host_port("not-a-url") is None


def test_probe_stream_reachable_success() -> None:
    with patch("app.services.camera_probe.socket.create_connection") as connect:
        connect.return_value.__enter__.return_value = None
        assert probe_stream_reachable("http://192.0.2.1/live", timeout=1.0) is True
        connect.assert_called_once_with(("192.0.2.1", 80), timeout=1.0)


def test_probe_stream_reachable_failure() -> None:
    with patch(
        "app.services.camera_probe.socket.create_connection",
        side_effect=OSError("refused"),
    ):
        assert probe_stream_reachable("rtsp://192.0.2.2/stream", timeout=1.0) is False


def test_probe_status_and_many() -> None:
    with patch(
        "app.services.camera_probe.probe_stream_reachable",
        return_value=True,
    ):
        assert probe_status("http://a") == "online"

    statuses = {
        "http://a": "online",
        "http://b": "offline",
    }
    with patch(
        "app.services.camera_probe.probe_status",
        side_effect=lambda url: statuses[url],
    ):
        assert probe_many_statuses(["http://a", "http://b"]) == ["online", "offline"]
