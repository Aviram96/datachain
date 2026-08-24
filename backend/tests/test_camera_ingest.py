"""Tests for camera stream ingest and chunking (Slice C / CP-C.P2–P4)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.camera import Camera
from app.models.user import User
from app.security.password import hash_password
from app.services.camera_ingest import (
    CameraIngestConfig,
    build_ffmpeg_receive_command,
    camera_chunk_dir,
    chunker_config_for_ingest,
    ingest_config_for_camera,
    ingest_configs_for_all_active,
)
from app.services.camera_stream import CameraNotFoundForStream, list_active_cameras
from app.services.segment_identity import camera_segment_pattern

import app.models as _models  # noqa: F401


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _user_with_cameras(db_session: Session) -> tuple[User, Camera, Camera]:
    user = User(email="ingest@example.com", password_hash=hash_password("password12"))
    db_session.add(user)
    db_session.flush()
    live = Camera(
        user_id=user.id,
        name="Front",
        stream_url="rtsp://192.0.2.50/live",
    )
    http = Camera(
        user_id=user.id,
        name="Lobby",
        stream_url="http://192.0.2.51/stream",
    )
    db_session.add_all([live, http])
    db_session.commit()
    return user, live, http


def test_build_ffmpeg_receive_command_rtsp_chunks_to_mp4(tmp_path: Path) -> None:
    camera_id = uuid4()
    config = CameraIngestConfig(
        camera_id=camera_id,
        stream_url="rtsp://192.0.2.50/live",
        temp_dir=tmp_path,
    )
    cmd = build_ffmpeg_receive_command(config)
    assert cmd[0] == "ffmpeg"
    assert "-rtsp_transport" in cmd
    assert cmd[cmd.index("-rtsp_transport") + 1] == "tcp"
    assert cmd[cmd.index("-i") + 1] == "rtsp://192.0.2.50/live"
    assert cmd[cmd.index("-f") + 1] == "segment"
    assert cmd[cmd.index("-segment_time") + 1] == "60"
    assert "-stream_loop" not in cmd
    out = str(camera_chunk_dir(camera_id, tmp_path) / f"{camera_id}_%Y%m%dT%H%M%SZ.mp4")
    assert out in cmd
    assert "-strftime" in cmd
    assert cmd[cmd.index("-strftime") + 1] == "1"


def test_build_ffmpeg_receive_command_http_skips_rtsp_flag(tmp_path: Path) -> None:
    config = CameraIngestConfig(
        camera_id=uuid4(),
        stream_url="https://192.0.2.51/stream",
        temp_dir=tmp_path,
    )
    cmd = build_ffmpeg_receive_command(config)
    assert "-rtsp_transport" not in cmd
    assert cmd[cmd.index("-i") + 1] == "https://192.0.2.51/stream"


def test_ingest_config_for_camera_attaches_url(db_session: Session) -> None:
    _user, live, _http = _user_with_cameras(db_session)
    config = ingest_config_for_camera(db_session, live.id)
    assert config.camera_id == live.id
    assert config.stream_url == "rtsp://192.0.2.50/live"
    assert config.segment_duration_seconds == 60


def test_ingest_config_rejects_unknown_camera(db_session: Session) -> None:
    with pytest.raises(CameraNotFoundForStream):
        ingest_config_for_camera(db_session, uuid4())


def test_ingest_configs_for_all_active_skips_deleted(db_session: Session) -> None:
    _user, live, http = _user_with_cameras(db_session)
    http.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    active = list_active_cameras(db_session)
    assert [camera.id for camera in active] == [live.id]

    configs = ingest_configs_for_all_active(db_session)
    assert len(configs) == 1
    assert configs[0].camera_id == live.id
    chunk = chunker_config_for_ingest(configs[0])
    assert chunk.temp_dir == camera_chunk_dir(live.id)
    assert chunk.input_uri == live.stream_url
    assert chunk.segment_duration_seconds == 60
    assert chunk.segment_pattern == camera_segment_pattern(live.id)
    assert chunk.strftime_output is True
