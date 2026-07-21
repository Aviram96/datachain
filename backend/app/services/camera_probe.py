"""Reachability probe for camera stream URLs (Slice B / CP-B.P4).

Status is ``online`` when the stream endpoint responds at the protocol layer
(HTTP/HTTPS request, or RTSP OPTIONS / TCP fallback), not merely when a
generic host ping succeeds without a stream scheme check.
"""

from __future__ import annotations

import socket
import urllib.error
import urllib.request
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


def _tcp_reachable(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_stream_reachable(stream_url: str, timeout: float) -> bool:
    """Treat any HTTP response (including 4xx/5xx) as a reachable stream host."""
    request = urllib.request.Request(
        stream_url,
        method="HEAD",
        headers={"User-Agent": "DatachainCameraProbe/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(0)
        return True
    except urllib.error.HTTPError:
        # Server answered — endpoint is reachable.
        return True
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        # Some servers reject HEAD; retry with a ranged GET.
        get_request = urllib.request.Request(
            stream_url,
            headers={
                "User-Agent": "DatachainCameraProbe/1.0",
                "Range": "bytes=0-0",
            },
        )
        try:
            with urllib.request.urlopen(get_request, timeout=timeout) as response:
                response.read(1)
            return True
        except urllib.error.HTTPError:
            return True
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            return False


def _rtsp_stream_reachable(host: str, port: int, timeout: float) -> bool:
    """Send a minimal RTSP OPTIONS request; fall back to TCP if the peer is silent."""
    if not _tcp_reachable(host, port, timeout):
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            # RTSP/1.0 OPTIONS is enough to prove a stream service is listening.
            payload = (
                f"OPTIONS rtsp://{host}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"User-Agent: DatachainCameraProbe/1.0\r\n"
                f"\r\n"
            ).encode("ascii")
            sock.sendall(payload)
            data = sock.recv(64)
            if data:
                return True
    except OSError:
        pass
    # TCP connected earlier; treat open RTSP port as reachable stream endpoint.
    return True


def probe_stream_reachable(
    stream_url: str,
    *,
    timeout: float | None = None,
) -> bool:
    """Return True when the camera stream endpoint appears reachable."""
    target = resolve_stream_host_port(stream_url)
    if target is None:
        return False
    host, port = target
    seconds = timeout if timeout is not None else get_camera_probe_timeout_seconds()
    scheme = (urlparse(stream_url).scheme or "").lower()

    if scheme in ("http", "https"):
        return _http_stream_reachable(stream_url, seconds)
    if scheme == "rtsp":
        return _rtsp_stream_reachable(host, port, seconds)
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
