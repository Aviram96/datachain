"""Receive a registered camera's live stream via FFmpeg (Slice C / CP-C.P2).

Chunking, unique segment names, and capture-offline handling are later Slice C
stories. This module keeps FFmpeg attached to ``stream_url`` so footage can be
processed continuously.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.camera_stream import (
    attach_camera_stream,
    get_active_camera,
    list_active_cameras,
)
from app.services.cctv_feed_simulator import DEFAULT_FFMPEG
from app.services.ffmpeg_supervisor import (
    FFmpegRunConfig,
    FFmpegSupervisor,
    resolve_max_restarts,
    resolve_restart_delay_seconds,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CameraIngestConfig:
    """Settings for receiving one camera stream."""

    camera_id: UUID
    stream_url: str
    ffmpeg_executable: str = DEFAULT_FFMPEG
    write_stdout: bool = True


def build_ffmpeg_receive_command(config: CameraIngestConfig) -> list[str]:
    """Build FFmpeg args: copy the live camera URL to MPEG-TS on stdout."""
    cmd = [
        config.ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "warning",
    ]
    if config.stream_url.lower().startswith("rtsp://"):
        cmd.extend(["-rtsp_transport", "tcp"])
    cmd.extend(
        [
            "-i",
            config.stream_url,
            "-c",
            "copy",
            "-f",
            "mpegts",
            "pipe:1",
        ]
    )
    return cmd


def ingest_config_for_camera(
    db: Session,
    camera_id: UUID,
    *,
    ffmpeg_executable: str = DEFAULT_FFMPEG,
    write_stdout: bool = True,
) -> CameraIngestConfig:
    """Attach an active camera and return ingest settings for its stream URL."""
    camera = get_active_camera(db, camera_id)
    stream_url = attach_camera_stream(db, camera_id)
    logger.info(
        "Attached camera %s (%s) at %s",
        camera.id,
        camera.name,
        stream_url,
    )
    return CameraIngestConfig(
        camera_id=camera.id,
        stream_url=stream_url,
        ffmpeg_executable=ffmpeg_executable,
        write_stdout=write_stdout,
    )


def ingest_configs_for_all_active(
    db: Session,
    *,
    ffmpeg_executable: str = DEFAULT_FFMPEG,
) -> list[CameraIngestConfig]:
    """Build ingest settings for every active camera (stdout discarded)."""
    cameras = list_active_cameras(db)
    configs: list[CameraIngestConfig] = []
    for camera in cameras:
        configs.append(
            ingest_config_for_camera(
                db,
                camera.id,
                ffmpeg_executable=ffmpeg_executable,
                write_stdout=False,
            )
        )
    return configs


class CameraIngest:
    """Run FFmpeg against one registered camera stream until stopped."""

    def __init__(self, config: CameraIngestConfig) -> None:
        self._config = config
        self._supervisor: FFmpegSupervisor | None = None

    @property
    def camera_id(self) -> UUID:
        return self._config.camera_id

    def stop(self) -> None:
        if self._supervisor is not None:
            self._supervisor.stop()

    def run_until_signal(self) -> int:
        """Receive the stream continuously; restart FFmpeg on crash."""
        stdout = sys.stdout.buffer if self._config.write_stdout else subprocess.DEVNULL
        logger.info(
            "Receiving stream for camera %s from %s (Ctrl+C to stop)",
            self._config.camera_id,
            self._config.stream_url,
        )
        run_config = FFmpegRunConfig(
            build_command=lambda: build_ffmpeg_receive_command(self._config),
            restart_on_crash=True,
            restart_delay_seconds=resolve_restart_delay_seconds(),
            max_restarts=resolve_max_restarts(),
            popen_kwargs={"stdout": stdout},
        )
        self._supervisor = FFmpegSupervisor(run_config)
        return self._supervisor.run_until_signal()
