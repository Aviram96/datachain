"""Background worker: process chunk files and remove them from temp/ on success."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from app.services.segment_integrity import SegmentIntegrityResult
from app.services.temp_chunk_cleanup import TempChunkCleanupError, delete_chunk
from app.services.video_chunker import DEFAULT_SEGMENT_PATTERN, list_chunk_files

logger = logging.getLogger(__name__)

ChunkProcessor = Callable[[Path], bool]
IntegrityCheck = Callable[[Path], SegmentIntegrityResult]


def stub_chunk_processor(path: Path) -> bool:
    """Placeholder until Epic 6 IPFS/chain/DB processing replaces it."""
    logger.info("Stub-processed chunk %s (Epic 6 will upload and anchor)", path.name)
    return True


@dataclass
class ChunkProcessingWorkerConfig:
    """Polling worker settings."""

    temp_dir: Path
    poll_interval_seconds: float = 1.0
    stable_delay_seconds: float = 0.5
    segment_pattern: str = DEFAULT_SEGMENT_PATTERN
    processor: ChunkProcessor = field(default=stub_chunk_processor)
    delete_on_success: bool = True
    integrity_check: IntegrityCheck | None = None


class ChunkProcessingWorker:
    """Poll temp/ for new chunk files; optionally integrity-check, then process.

    When ``delete_on_success`` is true (Epic 5 file-chunk cleanup), successful
    processing removes the file. Camera ingest uses the staging config
    (``delete_on_success=False``) so segments stay under temp/ until later
    processing succeeds (CP-C.P6). Deletion after success is CP-C.P7.
    """

    def __init__(self, config: ChunkProcessingWorkerConfig) -> None:
        self._config = config
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._handled: set[Path] = set()
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="chunk-processing-worker",
            daemon=True,
        )
        self._thread.start()
        role = "cleanup" if self._config.delete_on_success else "staging"
        logger.info(
            "Chunk %s worker watching %s (poll every %ss)",
            role,
            self._config.temp_dir,
            self._config.poll_interval_seconds,
        )

    def stop(self, *, flush: bool = True) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
        if flush:
            self._scan_once(final_pass=True)

    def process_all_blocking(self) -> int:
        """Process every stable chunk currently in temp/; return deleted count."""
        return self._scan_once(final_pass=True)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self._scan_once(final_pass=False)
            self._stop_event.wait(self._config.poll_interval_seconds)

    def _scan_once(self, *, final_pass: bool) -> int:
        deleted = 0
        if not self._config.temp_dir.is_dir():
            return 0
        for path in list_chunk_files(self._config.temp_dir, self._config.segment_pattern):
            with self._lock:
                if path in self._handled:
                    continue
            if not final_pass and not _is_file_stable(
                path,
                self._config.stable_delay_seconds,
            ):
                continue
            if self._config.integrity_check is not None:
                result = self._config.integrity_check(path)
                if not result.ok:
                    logger.error(
                        "Segment integrity failed for %s: %s",
                        path.name,
                        result.error,
                    )
                    with self._lock:
                        self._handled.add(path)
                    continue
                logger.info(
                    "Segment integrity ok %s sha256=%s bytes=%s",
                    path.name,
                    result.sha256,
                    result.size_bytes,
                )
            if not self._config.processor(path):
                logger.warning("Processing failed; keeping chunk %s", path.name)
                continue
            if self._config.delete_on_success:
                try:
                    delete_chunk(
                        path,
                        self._config.temp_dir,
                        self._config.segment_pattern,
                    )
                    deleted += 1
                except TempChunkCleanupError as exc:
                    logger.error("%s", exc)
                    continue
            with self._lock:
                self._handled.add(path)
        return deleted


def _is_file_stable(path: Path, delay_seconds: float) -> bool:
    """True when file size is unchanged after a short wait (write likely complete)."""
    try:
        first_size = path.stat().st_size
    except OSError:
        return False
    if first_size <= 0:
        return False
    time.sleep(delay_seconds)
    try:
        return path.stat().st_size == first_size
    except OSError:
        return False
