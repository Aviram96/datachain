"use client";

import Link from "next/link";
import { useState } from "react";

import type { CameraPublic, CameraStatus } from "@/lib/cameras-api";

type CameraCardProps = {
  camera: CameraPublic;
  onDelete: () => Promise<void>;
};

export function CameraCard({ camera, onDelete }: CameraCardProps) {
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function handleConfirmDelete() {
    setDeleting(true);
    try {
      await onDelete();
      setConfirming(false);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <article className="flex flex-col rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 space-y-1">
          <h2 className="text-lg font-medium text-white">{camera.name}</h2>
          <StatusBadge status={camera.status} />
        </div>
        <div className="flex shrink-0 gap-3 text-sm">
          <Link
            href={`/cameras/${camera.id}/edit`}
            className="text-emerald-400 hover:text-emerald-300"
          >
            Edit
          </Link>
          {!confirming ? (
            <button
              type="button"
              onClick={() => setConfirming(true)}
              className="text-red-400 hover:text-red-300"
            >
              Delete
            </button>
          ) : null}
        </div>
      </div>

      {confirming ? (
        <div className="mt-3 rounded-md border border-red-900/60 bg-red-950/30 p-3 text-sm">
          <p className="text-slate-200">
            Delete <span className="font-medium text-white">{camera.name}</span>
            ? This cannot be undone.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={deleting}
              onClick={() => void handleConfirmDelete()}
              className="rounded-md bg-red-700 px-3 py-1.5 text-white hover:bg-red-600 disabled:opacity-60"
            >
              {deleting ? "Deleting…" : "Delete"}
            </button>
            <button
              type="button"
              disabled={deleting}
              onClick={() => setConfirming(false)}
              className="rounded-md border border-slate-600 px-3 py-1.5 text-slate-300 hover:border-slate-500 disabled:opacity-60"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : null}

      <dl className="mt-3 space-y-2 text-sm">
        <div>
          <dt className="text-slate-500">Stream URL</dt>
          <dd className="truncate text-slate-300" title={camera.stream_url}>
            {camera.stream_url}
          </dd>
        </div>
        {camera.location ? (
          <div>
            <dt className="text-slate-500">Location</dt>
            <dd className="text-slate-300">{camera.location}</dd>
          </div>
        ) : null}
      </dl>
    </article>
  );
}

function StatusBadge({ status }: { status: CameraStatus }) {
  const online = status === "online";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ${
        online
          ? "bg-emerald-950/80 text-emerald-300 ring-1 ring-emerald-800/60"
          : "bg-slate-800 text-slate-400 ring-1 ring-slate-700"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          online ? "bg-emerald-400" : "bg-slate-500"
        }`}
        aria-hidden
      />
      {online ? "Online" : "Offline"}
    </span>
  );
}
