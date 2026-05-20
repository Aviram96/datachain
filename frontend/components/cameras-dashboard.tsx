"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { networkErrorMessage } from "@/lib/api";
import {
  CamerasApiError,
  deleteCamera,
  listCameras,
  type CameraPublic,
} from "@/lib/cameras-api";

import { CameraCard } from "./camera-card";
import { useToast } from "./toast-provider";

const PAGE_SIZE = 10;

export function CamerasDashboard() {
  const { showToast } = useToast();
  const [cameras, setCameras] = useState<CameraPublic[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  const loadCameras = useCallback(
    async (pageToLoad: number) => {
      setLoading(true);
      try {
        const data = await listCameras(pageToLoad, PAGE_SIZE);
        setCameras(data.items);
        setTotal(data.total);
        setPage(data.page);
        setPages(data.pages);
      } catch (error) {
        if (error instanceof CamerasApiError) {
          showToast(error.message, "error");
        } else {
          showToast(networkErrorMessage(), "error");
        }
      } finally {
        setLoading(false);
      }
    },
    [showToast]
  );

  useEffect(() => {
    void loadCameras(page);
  }, [loadCameras, page]);

  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteCamera(id);
        showToast("Camera removed.", "success");
        if (cameras.length === 1 && page > 1) {
          setPage((current) => current - 1);
        } else {
          await loadCameras(page);
        }
      } catch (error) {
        if (error instanceof CamerasApiError) {
          showToast(error.message, "error");
        } else {
          showToast(networkErrorMessage(), "error");
        }
        throw error;
      }
    },
    [cameras.length, loadCameras, page, showToast]
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Cameras</h1>
          <p className="text-sm text-slate-400">
            {loading
              ? "Loading…"
              : total === 0
                ? "No cameras yet."
                : `${total} camera${total === 1 ? "" : "s"}`}
          </p>
        </div>
        <Link
          href="/cameras/new"
          className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
        >
          Add camera
        </Link>
      </div>

      {loading ? (
        <p className="text-slate-400">Loading cameras…</p>
      ) : cameras.length === 0 ? (
        <p className="rounded-lg border border-dashed border-slate-700 p-8 text-center text-slate-400">
          Add your first camera to start monitoring streams.
        </p>
      ) : (
        <CamerasGrid cameras={cameras} onDelete={handleDelete} />
      )}

      <PaginationControls
        page={page}
        pages={pages}
        total={total}
        pageSize={PAGE_SIZE}
        loading={loading}
        onPageChange={setPage}
      />
    </div>
  );
}

function PaginationControls({
  page,
  pages,
  total,
  pageSize,
  loading,
  onPageChange,
}: {
  page: number;
  pages: number;
  total: number;
  pageSize: number;
  loading: boolean;
  onPageChange: (page: number) => void;
}) {
  if (pages <= 1 || total === 0) {
    return null;
  }

  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-800 pt-4">
      <p className="text-sm text-slate-500">
        Showing {start}–{end} of {total} cameras
      </p>
      <div className="flex items-center gap-3">
        <button
          type="button"
          disabled={page <= 1 || loading}
          onClick={() => onPageChange(page - 1)}
          className="rounded-md border border-slate-600 px-3 py-1.5 text-sm text-slate-300 hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-sm text-slate-400">
          Page {page} of {pages}
        </span>
        <button
          type="button"
          disabled={page >= pages || loading}
          onClick={() => onPageChange(page + 1)}
          className="rounded-md border border-slate-600 px-3 py-1.5 text-sm text-slate-300 hover:border-slate-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}

function CamerasGrid({
  cameras,
  onDelete,
}: {
  cameras: CameraPublic[];
  onDelete: (id: string) => Promise<void>;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {cameras.map((camera) => (
        <CameraCard
          key={camera.id}
          camera={camera}
          onDelete={() => onDelete(camera.id)}
        />
      ))}
    </div>
  );
}
