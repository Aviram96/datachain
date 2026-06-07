"""Tests for chunk processing worker."""

from __future__ import annotations

from pathlib import Path

from app.services.chunk_processing_worker import (
    ChunkProcessingWorker,
    ChunkProcessingWorkerConfig,
)


def test_worker_deletes_on_success(tmp_path: Path) -> None:
    chunk = tmp_path / "chunk_000.mp4"
    chunk.write_bytes(b"data")

    worker = ChunkProcessingWorker(
        ChunkProcessingWorkerConfig(
            temp_dir=tmp_path,
            stable_delay_seconds=0,
        ),
    )
    deleted = worker.process_all_blocking()
    assert deleted == 1
    assert not chunk.exists()


def test_worker_keeps_file_on_processor_failure(tmp_path: Path) -> None:
    chunk = tmp_path / "chunk_000.mp4"
    chunk.write_bytes(b"data")

    def fail_processor(_path: Path) -> bool:
        return False

    worker = ChunkProcessingWorker(
        ChunkProcessingWorkerConfig(
            temp_dir=tmp_path,
            stable_delay_seconds=0,
            processor=fail_processor,
        ),
    )
    deleted = worker.process_all_blocking()
    assert deleted == 0
    assert chunk.exists()
