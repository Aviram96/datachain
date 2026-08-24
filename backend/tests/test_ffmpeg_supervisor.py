"""Tests for FFmpeg supervisor restart behavior."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.ffmpeg_supervisor import (
    FFmpegRunConfig,
    FFmpegSupervisor,
    resolve_max_restarts,
    resolve_restart_delay_seconds,
)


def test_resolve_restart_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("CCTV_FFMPEG_RESTART_DELAY_SECONDS", raising=False)
    monkeypatch.delenv("CCTV_FFMPEG_MAX_RESTARTS", raising=False)
    assert resolve_restart_delay_seconds() == 2.0
    assert resolve_max_restarts() is None


def test_supervisor_restarts_after_crash() -> None:
    processes = [
        MagicMock(wait=MagicMock(return_value=1), stderr=None, poll=MagicMock(return_value=1)),
        MagicMock(wait=MagicMock(return_value=0), stderr=None, poll=MagicMock(return_value=0)),
    ]
    build_count = {"n": 0}

    def build_command() -> list[str]:
        build_count["n"] += 1
        return ["ffmpeg", "-version"]

    config = FFmpegRunConfig(
        build_command=build_command,
        restart_on_crash=True,
        restart_delay_seconds=0,
    )
    supervisor = FFmpegSupervisor(config)

    with patch("app.services.ffmpeg_supervisor.subprocess.Popen", side_effect=processes):
        code = supervisor.run_until_signal()

    assert code == 0
    assert supervisor.restart_count == 1
    assert build_count["n"] == 2


def test_supervisor_does_not_restart_on_success() -> None:
    proc = MagicMock(wait=MagicMock(return_value=0), stderr=None, poll=MagicMock(return_value=0))
    build_count = {"n": 0}

    def build_command() -> list[str]:
        build_count["n"] += 1
        return ["ffmpeg"]

    config = FFmpegRunConfig(build_command=build_command, restart_on_crash=True)
    supervisor = FFmpegSupervisor(config)

    with patch("app.services.ffmpeg_supervisor.subprocess.Popen", return_value=proc):
        code = supervisor.run_until_signal()

    assert code == 0
    assert supervisor.restart_count == 0
    assert supervisor.gave_up_after_restarts is False
    assert build_count["n"] == 1


def test_supervisor_respects_max_restarts() -> None:
    proc = MagicMock(wait=MagicMock(return_value=1), stderr=None, poll=MagicMock(return_value=1))
    config = FFmpegRunConfig(
        build_command=lambda: ["ffmpeg"],
        restart_on_crash=True,
        restart_delay_seconds=0,
        max_restarts=2,
    )
    supervisor = FFmpegSupervisor(config)

    with patch("app.services.ffmpeg_supervisor.subprocess.Popen", return_value=proc):
        code = supervisor.run_until_signal()

    assert code == 1
    assert supervisor.restart_count == 2
    assert supervisor.gave_up_after_restarts is True
