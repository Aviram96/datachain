"""Tests for camera stream ingest (Slice C / CP-C.P2; no real FFmpeg)."""

from __future__ import annotations

from datetime import datetime, timezone
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
    ingest_config_for_camera,
    ingest_configs_for_all_active,
)
from app.services.camera_stream import CameraNotFoundForStream, list_active_cameras

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


def test_build_ffmpeg_receive_command_rtsp_uses_tcp() -> None:
    config = CameraIngestConfig(
        camera_id=uuid4(),
        stream_url="rtsp://192.0.2.50/live",
    )
    cmd = build_ffmpeg_receive_command(config)
    assert cmd[0] == "ffmpeg"
    assert "-rtsp_transport" in cmd
    assert cmd[cmd.index("-rtsp_transport") + 1] == "tcp"
    assert cmd[cmd.index("-i") + 1] == "rtsp://192.0.2.50/live"
    assert cmd[-2:] == ["mpegts", "pipe:1"]
    assert "-stream_loop" not in cmd


def test_build_ffmpeg_receive_command_http_skips_rtsp_flag() -> None:
    config = CameraIngestConfig(
        camera_id=uuid4(),
        stream_url="https://192.0.2.51/stream",
    )
    cmd = build_ffmpeg_receive_command(config)
    assert "-rtsp_transport" not in cmd
    assert cmd[cmd.index("-i") + 1] == "https://192.0.2.51/stream"


def test_ingest_config_for_camera_attaches_url(db_session: Session) -> None:
    _user, live, _http = _user_with_cameras(db_session)
    config = ingest_config_for_camera(db_session, live.id)
    assert config.camera_id == live.id
    assert config.stream_url == "rtsp://192.0.2.50/live"
    assert config.write_stdout is True


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
    assert configs[0].write_stdout is False
