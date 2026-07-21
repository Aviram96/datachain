"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { useToast } from "@/components/toast-provider";
import { networkErrorMessage } from "@/lib/api";
import {
  CamerasApiError,
  deleteCamera,
  getCamera,
  type CameraPublic,
} from "@/lib/cameras-api";

export default function CameraDetailPage() {
  return (
    <RequireAuth>
      <CameraDetailContent />
    </RequireAuth>
  );
}

function CameraDetailContent() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  const cameraId = String(params.id ?? "");

  const [camera, setCamera] = useState<CameraPublic | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getCamera(cameraId);
      setCamera(data);
    } catch (error) {
      if (error instanceof CamerasApiError) {
        showToast(error.message, "error");
      } else {
        showToast(networkErrorMessage(), "error");
      }
      setCamera(null);
    } finally {
      setLoading(false);
    }
  }, [cameraId, showToast]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleDelete() {
    setDeleting(true);
    try {
      await deleteCamera(cameraId);
      showToast("Camera removed from your dashboard.", "success");
      router.push("/cameras");
    } catch (error) {
      if (error instanceof CamerasApiError) {
        showToast(error.message, "error");
      } else {
        showToast(networkErrorMessage(), "error");
      }
    } finally {
      setDeleting(false);
    }
  }

  if (loading) {
    return <p className="text-slate-400">Loading camera…</p>;
  }

  if (!camera) {
    return (
      <div className="space-y-4">
        <Link href="/cameras" className="text-sm text-slate-400 hover:text-slate-200">
          ← Cameras
        </Link>
        <p className="text-slate-300">Camera not found.</p>
      </div>
    );
  }

  const online = camera.status === "online";

  return (
    <div className="space-y-6">
      <div>
        <Link href="/cameras" className="text-sm text-slate-400 hover:text-slate-200">
          ← Cameras
        </Link>
        <div className="mt-2 flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold text-white">{camera.name}</h1>
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ${
                online
                  ? "bg-emerald-950/80 text-emerald-300 ring-1 ring-emerald-800/60"
                  : "bg-slate-800 text-slate-400 ring-1 ring-slate-700"
              }`}
            >
              {online ? "Online" : "Offline"}
            </span>
          </div>
          <div className="flex flex-wrap gap-3 text-sm">
            <Link
              href={`/cameras/${camera.id}/edit`}
              className="rounded-md border border-slate-600 px-3 py-1.5 text-slate-200 hover:border-slate-500"
            >
              Edit
            </Link>
            {!confirmingDelete ? (
              <button
                type="button"
                onClick={() => setConfirmingDelete(true)}
                className="rounded-md border border-red-800 px-3 py-1.5 text-red-300 hover:border-red-700"
              >
                Delete
              </button>
            ) : null}
          </div>
        </div>
      </div>

      {confirmingDelete ? (
        <div className="rounded-md border border-red-900/60 bg-red-950/30 p-4 text-sm">
          <p className="text-slate-200">
            Remove this camera from your dashboard? Historical recordings stay
            available for evidence.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={deleting}
              onClick={() => void handleDelete()}
              className="rounded-md bg-red-700 px-3 py-1.5 text-white hover:bg-red-600 disabled:opacity-60"
            >
              {deleting ? "Removing…" : "Remove"}
            </button>
            <button
              type="button"
              disabled={deleting}
              onClick={() => setConfirmingDelete(false)}
              className="rounded-md border border-slate-600 px-3 py-1.5 text-slate-300 hover:border-slate-500 disabled:opacity-60"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : null}

      <dl className="space-y-3 rounded-lg border border-slate-800 bg-slate-900/50 p-4 text-sm">
        <div>
          <dt className="text-slate-500">Stream URL</dt>
          <dd className="break-all text-slate-200">{camera.stream_url}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Location</dt>
          <dd className="text-slate-200">{camera.location || "—"}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Added</dt>
          <dd className="text-slate-200">
            {new Date(camera.created_at).toLocaleString()}
          </dd>
        </div>
      </dl>

      <section className="space-y-2 rounded-lg border border-dashed border-slate-700 p-4">
        <h2 className="text-lg font-medium text-white">Recordings</h2>
        <p className="text-sm text-slate-400">
          Search, watch, download, and verify videos for this camera will appear
          here (Slice E — Video management).
        </p>
      </section>
    </div>
  );
}
