"""Tests for ingest staging under temp/ until processing succeeds (CP-C.P6)."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.services.camera_ingest import (
    CameraIngestConfig,
    camera_chunk_dir,
    integrity_worker_config_for_ingest,
)
from app.services.chunk_processing_worker import ChunkProcessingWorker
from app.services.segment_identity import camera_segment_pattern
from app.services.segment_integrity import SegmentIntegrityResult
from app.services.segment_staging import (
    is_under_staging_dir,
    keep_staged_until_processing_succeeds,
    staging_dir_for_camera,
    staging_worker_config,
)

CAMERA_ID = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")


def _box(box_type: bytes, payload: bytes) -> bytes:
    size = 8 + len(payload)
    return size.to_bytes(4, "big") + box_type + payload


def _minimal_mp4() -> bytes:
    ftyp = _box(b"ftyp", b"isom" + (0).to_bytes(4, "big") + b"isom")
    moov = _box(b"moov", b"")
    return ftyp + moov


def test_staging_dir_for_camera_is_under_temp(tmp_path: Path) -> None:
    staged = staging_dir_for_camera(CAMERA_ID, tmp_path)
    assert staged == (tmp_path / str(CAMERA_ID)).resolve()
    assert staged == camera_chunk_dir(CAMERA_ID, tmp_path)
    assert staged.parent == tmp_path.resolve()


def test_is_under_staging_dir_rejects_outside(tmp_path: Path) -> None:
    staging = staging_dir_for_camera(CAMERA_ID, tmp_path)
    staging.mkdir()
    inside = staging / f"{CAMERA_ID}_20260824T120000Z.mp4"
    inside.write_bytes(_minimal_mp4())
    outside = tmp_path / "other.mp4"
    outside.write_bytes(_minimal_mp4())
    assert is_under_staging_dir(inside, staging) is True
    assert is_under_staging_dir(outside, staging) is False


def test_staging_worker_keeps_file_after_processor_success(tmp_path: Path) -> None:
    staging = staging_dir_for_camera(CAMERA_ID, tmp_path)
    staging.mkdir()
    segment = staging / f"{CAMERA_ID}_20260824T120000Z.mp4"
    segment.write_bytes(_minimal_mp4())

    def pass_check(path: Path) -> SegmentIntegrityResult:
        return SegmentIntegrityResult(ok=True, path=path, sha256="abc", size_bytes=1)

    worker = ChunkProcessingWorker(
        staging_worker_config(
            temp_dir=staging,
            segment_pattern=camera_segment_pattern(CAMERA_ID),
            integrity_check=pass_check,
            stable_delay_seconds=0,
        )
    )
    deleted = worker.process_all_blocking()
    assert deleted == 0
    assert segment.exists()
    assert is_under_staging_dir(segment, staging)


def test_ingest_worker_config_uses_staging_contract(tmp_path: Path) -> None:
    config = CameraIngestConfig(
        camera_id=CAMERA_ID,
        stream_url="rtsp://192.0.2.50/live",
        temp_dir=tmp_path,
    )
    worker_config = integrity_worker_config_for_ingest(config)
    assert worker_config.temp_dir == staging_dir_for_camera(CAMERA_ID, tmp_path)
    assert worker_config.delete_on_success is False
    assert worker_config.processor is keep_staged_until_processing_succeeds
    assert worker_config.segment_pattern == camera_segment_pattern(CAMERA_ID)
