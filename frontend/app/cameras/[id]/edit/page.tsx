"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { CameraForm } from "@/components/camera-form";
import { RequireAuth } from "@/components/require-auth";
import { useToast } from "@/components/toast-provider";
import { networkErrorMessage } from "@/lib/api";
import {
  CamerasApiError,
  getCamera,
  updateCamera,
  type CameraPublic,
} from "@/lib/cameras-api";

export default function EditCameraPage() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  const cameraId = typeof params.id === "string" ? params.id : "";

  const [camera, setCamera] = useState<CameraPublic | null>(null);
  const [loading, setLoading] = useState(true);

  const loadCamera = useCallback(async () => {
    if (!cameraId) {
      setLoading(false);
      return;
    }
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
      router.replace("/cameras");
    } finally {
      setLoading(false);
    }
  }, [cameraId, router, showToast]);

  useEffect(() => {
    void loadCamera();
  }, [loadCamera]);

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div>
          <Link
            href={`/cameras/${cameraId}`}
            className="text-sm text-slate-400 hover:text-slate-200"
          >
            ← Camera
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-white">
            Edit camera
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Update name, stream URL, or location.
          </p>
        </div>

        {loading ? (
          <p className="text-slate-400">Loading camera…</p>
        ) : camera ? (
          <CameraForm
            key={camera.id}
            submitLabel="Save changes"
            initialValues={{
              name: camera.name,
              stream_url: camera.stream_url,
              location: camera.location,
            }}
            onCancel={() => router.push(`/cameras/${camera.id}`)}
            onSubmit={async (payload) => {
              try {
                await updateCamera(camera.id, payload);
                showToast("Camera updated.", "success");
                router.push(`/cameras/${camera.id}`);
              } catch (error) {
                if (error instanceof CamerasApiError) {
                  showToast(error.message, "error");
                } else {
                  showToast(networkErrorMessage(), "error");
                }
                throw error;
              }
            }}
          />
        ) : (
          <p className="text-slate-400">Camera not found.</p>
        )}
      </div>
    </RequireAuth>
  );
}
