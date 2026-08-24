#!/usr/bin/env python3
"""CLI: receive registered camera streams and write 1-minute MP4 segments.

Run from backend/ with the venv activated and Postgres available:

    python scripts/ingest_camera.py --camera-id UUID
    python scripts/ingest_camera.py --all

Requires FFmpeg on PATH (https://ffmpeg.org/download.html).
"""

from __future__ import annotations

import argparse
import logging
import sys
import threading
import time
from uuid import UUID

from app.db.session import get_sessionmaker
from app.services.camera_ingest import (
    CameraIngest,
    CameraIngestConfig,
    ingest_config_for_camera,
    ingest_configs_for_all_active,
)
from app.services.camera_stream import CameraStreamError
from app.services.cctv_feed_simulator import DEFAULT_FFMPEG
from app.services.video_chunker import resolve_chunk_duration_seconds, resolve_temp_dir

import app.models  # noqa: F401  — register ORM mappers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Receive camera streams and split them into 1-minute MP4 segments.",
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--camera-id",
        metavar="UUID",
        help="Ingest one active camera by id",
    )
    target.add_argument(
        "--all",
        action="store_true",
        help="Ingest every active (non-deleted) camera",
    )
    parser.add_argument(
        "--ffmpeg",
        metavar="EXE",
        default=DEFAULT_FFMPEG,
        help="FFmpeg executable name or path (default: ffmpeg)",
    )
    parser.add_argument(
        "--temp-dir",
        "-t",
        metavar="DIR",
        help="Base temp directory (default backend/temp; each camera gets a subfolder)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        metavar="SECONDS",
        help="Segment length in seconds (default 60)",
    )
    return parser.parse_args(argv)


def _run_one(config: CameraIngestConfig) -> int:
    return CameraIngest(config).run_until_signal()


def _run_all(configs: list[CameraIngestConfig]) -> int:
    if not configs:
        logging.error("No active cameras to ingest.")
        return 1
    ingests = [CameraIngest(config) for config in configs]
    threads = [
        threading.Thread(
            target=ingest.run_until_signal,
            name=f"ingest-{ingest.camera_id}",
            daemon=True,
        )
        for ingest in ingests
    ]
    for thread in threads:
        thread.start()
    logging.info("Chunking %s camera stream(s); Ctrl+C to stop", len(ingests))
    try:
        while any(thread.is_alive() for thread in threads):
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Stopping camera ingest")
        for ingest in ingests:
            ingest.stop()
        for thread in threads:
            thread.join(timeout=10)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    ffmpeg = args.ffmpeg.strip() or DEFAULT_FFMPEG
    temp_dir = resolve_temp_dir(args.temp_dir)
    duration = resolve_chunk_duration_seconds(args.duration)
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    one: CameraIngestConfig | None = None
    many: list[CameraIngestConfig] | None = None
    try:
        if args.camera_id:
            camera_id = UUID(args.camera_id)
            one = ingest_config_for_camera(
                db,
                camera_id,
                ffmpeg_executable=ffmpeg,
                temp_dir=temp_dir,
                segment_duration_seconds=duration,
            )
        else:
            many = ingest_configs_for_all_active(
                db,
                ffmpeg_executable=ffmpeg,
                temp_dir=temp_dir,
                segment_duration_seconds=duration,
            )
    except CameraStreamError as exc:
        logging.error("%s", exc)
        return 1
    except ValueError:
        logging.error("Invalid camera id: %s", args.camera_id)
        return 1
    finally:
        db.close()

    try:
        if one is not None:
            return _run_one(one)
        return _run_all(many or [])
    except FileNotFoundError:
        logging.error(
            "FFmpeg not found (%r). Install FFmpeg and ensure it is on PATH.",
            ffmpeg,
        )
        return 127


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
