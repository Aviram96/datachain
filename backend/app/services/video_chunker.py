"""Split video input into fixed-duration MP4 segments under backend/temp/."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.cctv_feed_simulator import (
    DEFAULT_FFMPEG,
    validate_source_mp4,
)

logger = logging.getLogger(__name__)

ENV_TEMP_DIR = "CCTV_TEMP_DIR"
ENV_CHUNK_DURATION_SECONDS = "CCTV_CHUNK_DURATION_SECONDS"
DEFAULT_CHUNK_DURATION_SECONDS = 60
DEFAULT_SEGMENT_PATTERN = "chunk_%03d.mp4"
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class VideoChunkerError(Exception):
    """Invalid chunker configuration or runtime failure."""


@dataclass(frozen=True)
class VideoChunkerConfig:
    """Settings for FFmpeg segment output."""

    source_path: Path
    temp_dir: Path
    segment_duration_seconds: int = DEFAULT_CHUNK_DURATION_SECONDS
    ffmpeg_executable: str = DEFAULT_FFMPEG
    loop_source: bool = False
    segment_pattern: str = DEFAULT_SEGMENT_PATTERN


def resolve_temp_dir(cli_path: str | None = None) -> Path:
    """Resolve output directory from CLI flag, then CCTV_TEMP_DIR, then backend/temp."""
    if cli_path and cli_path.strip():
        return Path(cli_path.strip()).expanduser().resolve()
    env_path = os.getenv(ENV_TEMP_DIR, "").strip()
    if env_path:
        return Path(env_path).expanduser().resolve()
    return (BACKEND_ROOT / "temp").resolve()


def resolve_chunk_duration_seconds(cli_value: int | None = None) -> int:
    """Resolve segment length; default 60 seconds (1 minute)."""
    if cli_value is not None:
        return _clamp_chunk_duration(cli_value)
    raw = os.getenv(ENV_CHUNK_DURATION_SECONDS, "").strip()
    if raw:
        try:
            return _clamp_chunk_duration(int(raw))
        except ValueError:
            pass
    return DEFAULT_CHUNK_DURATION_SECONDS


def _clamp_chunk_duration(seconds: int) -> int:
    if seconds < 1:
        raise VideoChunkerError("Chunk duration must be at least 1 second")
    return min(seconds, 3600)


def ensure_temp_dir(path: Path) -> Path:
    """Create temp directory if missing."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def segment_output_path(config: VideoChunkerConfig) -> Path:
    """Full path template passed to FFmpeg segment muxer."""
    return config.temp_dir / config.segment_pattern


def build_ffmpeg_chunk_command(config: VideoChunkerConfig) -> list[str]:
    """Build FFmpeg args: segment muxer, MP4 chunks of fixed duration."""
    cmd = [
        config.ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "warning",
    ]
    if config.loop_source:
        cmd.extend(["-re", "-stream_loop", "-1"])
    cmd.extend(
        [
            "-i",
            str(config.source_path),
            "-c",
            "copy",
            "-f",
            "segment",
            "-segment_time",
            str(config.segment_duration_seconds),
            "-reset_timestamps",
            "1",
            "-segment_format",
            "mp4",
            str(segment_output_path(config)),
        ]
    )
    return cmd


def list_chunk_files(temp_dir: Path, pattern: str = DEFAULT_SEGMENT_PATTERN) -> list[Path]:
    """Return chunk files matching the segment naming pattern, sorted by name."""
    prefix = pattern.split("%")[0]
    suffix = ".mp4"
    files = [
        path
        for path in temp_dir.iterdir()
        if path.is_file() and path.name.startswith(prefix) and path.suffix == suffix
    ]
    return sorted(files, key=lambda path: path.name)


class VideoChunker:
    """Run FFmpeg that writes fixed-duration MP4 segments to temp/."""

    def __init__(self, config: VideoChunkerConfig) -> None:
        self._config = config
        self._process: subprocess.Popen[bytes] | None = None
        self._stopped = False

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> None:
        if self.is_running:
            raise VideoChunkerError("Chunker is already running")
        validate_source_mp4(self._config.source_path)
        ensure_temp_dir(self._config.temp_dir)
        cmd = build_ffmpeg_chunk_command(self._config)
        mode = "looping" if self._config.loop_source else "one pass"
        logger.info(
            "Chunking %s into %ss segments under %s (%s; Ctrl+C to stop)",
            self._config.source_path,
            self._config.segment_duration_seconds,
            self._config.temp_dir,
            mode,
        )
        self._process = subprocess.Popen(cmd, stderr=subprocess.PIPE)

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        proc = self._process
        if proc is None or proc.poll() is not None:
            return
        logger.info("Stopping video chunker")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    def wait(self) -> int:
        if self._process is None:
            return 0
        return self._process.wait()

    def run_until_signal(self) -> int:
        """Start, handle SIGINT/SIGTERM, stop cleanly, return FFmpeg exit code."""
        previous_handlers: dict[int, Any] = {}

        def _handle_signal(signum: int, _frame: object | None) -> None:
            logger.info("Received signal %s; shutting down chunker", signum)
            self.stop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                previous_handlers[sig] = signal.signal(sig, _handle_signal)
            except (ValueError, OSError):
                pass

        try:
            self.start()
            code = self.wait()
            if self._process and self._process.stderr:
                err = self._process.stderr.read().decode("utf-8", errors="replace")
                if err.strip():
                    logger.warning("FFmpeg stderr:\n%s", err.strip())
            chunks = list_chunk_files(
                self._config.temp_dir,
                self._config.segment_pattern,
            )
            logger.info("Wrote %d chunk file(s) to %s", len(chunks), self._config.temp_dir)
            return code
        finally:
            self.stop()
            for sig, handler in previous_handlers.items():
                try:
                    signal.signal(sig, handler)
                except (ValueError, OSError):
                    pass
