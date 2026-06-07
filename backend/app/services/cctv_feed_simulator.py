"""Loop a local MP4 as a continuous CCTV-style feed via FFmpeg (no chunking yet)."""

from __future__ import annotations

import logging
from typing import Any
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

ENV_SOURCE_MP4 = "CCTV_SOURCE_MP4"
DEFAULT_FFMPEG = "ffmpeg"


class CctvFeedError(Exception):
    """Invalid configuration or simulator state."""


@dataclass(frozen=True)
class CctvFeedConfig:
    """Settings for the looping feed subprocess."""

    source_path: Path
    ffmpeg_executable: str = DEFAULT_FFMPEG


def resolve_source_path(cli_path: str | None = None) -> Path:
    """Resolve MP4 path from CLI flag, then CCTV_SOURCE_MP4 env."""
    if cli_path and cli_path.strip():
        return Path(cli_path.strip()).expanduser().resolve()
    env_path = os.getenv(ENV_SOURCE_MP4, "").strip()
    if env_path:
        return Path(env_path).expanduser().resolve()
    raise CctvFeedError(
        "No source MP4 configured. Pass --source PATH or set "
        f"{ENV_SOURCE_MP4} in the environment (see backend/.env.example)."
    )


def validate_source_mp4(path: Path) -> None:
    """Ensure the file exists and is an .mp4 (case-insensitive)."""
    if not path.is_file():
        raise CctvFeedError(f"Source file not found: {path}")
    if path.suffix.lower() != ".mp4":
        raise CctvFeedError(
            f"Source must be a .mp4 file (got {path.suffix!r}): {path}"
        )


def build_ffmpeg_loop_command(config: CctvFeedConfig) -> list[str]:
    """Build FFmpeg args: real-time pace, infinite loop, MPEG-TS to stdout."""
    return [
        config.ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "warning",
        "-re",
        "-stream_loop",
        "-1",
        "-i",
        str(config.source_path),
        "-c",
        "copy",
        "-f",
        "mpegts",
        "pipe:1",
    ]


class CctvFeedSimulator:
    """Run FFmpeg that loops one MP4 like a live CCTV source."""

    def __init__(self, config: CctvFeedConfig) -> None:
        self._config = config
        self._process: subprocess.Popen[bytes] | None = None
        self._stopped = False

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> None:
        if self.is_running:
            raise CctvFeedError("Simulator is already running")
        validate_source_mp4(self._config.source_path)
        cmd = build_ffmpeg_loop_command(self._config)
        logger.info(
            "Starting CCTV feed simulation from %s (Ctrl+C to stop)",
            self._config.source_path,
        )
        self._process = subprocess.Popen(
            cmd,
            stdout=sys.stdout.buffer,
            stderr=subprocess.PIPE,
        )

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        proc = self._process
        if proc is None or proc.poll() is not None:
            return
        logger.info("Stopping CCTV feed simulation")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    def wait(self) -> int:
        """Block until FFmpeg exits; return its exit code (0 if not started)."""
        if self._process is None:
            return 0
        return self._process.wait()

    def run_until_signal(self) -> int:
        """Start, handle SIGINT/SIGTERM, stop cleanly, return FFmpeg exit code."""
        previous_handlers: dict[int, Any] = {}

        def _handle_signal(signum: int, _frame: object | None) -> None:
            logger.info("Received signal %s; shutting down feed", signum)
            self.stop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                previous_handlers[sig] = signal.signal(sig, _handle_signal)
            except (ValueError, OSError):
                # SIGTERM not always available (e.g. some Windows builds)
                pass

        try:
            self.start()
            code = self.wait()
            if self._process and self._process.stderr:
                err = self._process.stderr.read().decode("utf-8", errors="replace")
                if err.strip():
                    logger.warning("FFmpeg stderr:\n%s", err.strip())
            return code
        finally:
            self.stop()
            for sig, handler in previous_handlers.items():
                try:
                    signal.signal(sig, handler)
                except (ValueError, OSError):
                    pass
