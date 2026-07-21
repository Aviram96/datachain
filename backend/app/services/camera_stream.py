"""Resolve registered camera streams for ingest (Slice B / CP-B.P5).

Continuous chunking and FFmpeg supervision live in Slice C; this module is the
attach point that returns an active camera's ``stream_url`` for processing.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.camera import Camera


class CameraStreamError(Exception):
    """Raised when a camera stream cannot be attached for ingest."""


class CameraNotFoundForStream(CameraStreamError):
    """No active (non-deleted) camera exists for the given id."""


def get_active_camera(db: Session, camera_id: UUID) -> Camera:
    """Return an active camera row or raise ``CameraNotFoundForStream``."""
    camera = db.execute(
        select(Camera).where(
            Camera.id == camera_id,
            Camera.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if camera is None:
        raise CameraNotFoundForStream(f"Active camera not found: {camera_id}")
    return camera


def attach_camera_stream(db: Session, camera_id: UUID) -> str:
    """Return the stream URL for an active registered camera.

    Callers (Slice C pipeline) use this URL with FFmpeg / chunking. Soft-deleted
    cameras are not attachable.
    """
    return get_active_camera(db, camera_id).stream_url
