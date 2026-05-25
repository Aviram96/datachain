"""Reachability probe for camera stream URLs (US-4.6)."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Literal
from urllib.parse import urlparse

from app.config import get_camera_probe_timeout_seconds

DEFAULT_PORTS: dict[str, int] = {
    "http": 80,
    "https": 443,
    "rtsp": 554,
}


def resolve_stream_host_port(stream_url: str) -> tuple[str, int] | None:
    """Parse a supported stream URL into host and port, or None if invalid."""
    parsed = urlparse(stream_url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in DEFAULT_PORTS:
        return None
    host = parsed.hostname
    if not host:
        return None
    port = parsed.port if parsed.port is not None else DEFAULT_PORTS[scheme]
    return host, port


def probe_stream_reachable(
    stream_url: str,
    *,
    timeout: float | None = None,
) -> bool:
    """Return True when a TCP connection to the stream host:port succeeds."""
    target = resolve_stream_host_port(stream_url)
    if target is None:
        return False
    host, port = target
    seconds = timeout if timeout is not None else get_camera_probe_timeout_seconds()
    try:
        with socket.create_connection((host, port), timeout=seconds):
            return True
    except OSError:
        return False


def probe_status(stream_url: str) -> Literal["online", "offline"]:
    """Return ``online`` or ``offline`` for a stream URL."""
    return "online" if probe_stream_reachable(stream_url) else "offline"


def probe_many_statuses(
    stream_urls: list[str],
) -> list[Literal["online", "offline"]]:
    """Probe multiple stream URLs concurrently; order matches input."""
    if not stream_urls:
        return []
    workers = min(len(stream_urls), 10)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(probe_status, stream_urls))
