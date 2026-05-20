import Link from "next/link";

import type { CameraPublic } from "@/lib/cameras-api";

type CameraCardProps = {
  camera: CameraPublic;
};

export function CameraCard({ camera }: CameraCardProps) {
  return (
    <article className="flex flex-col rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-start justify-between gap-2">
        <h2 className="text-lg font-medium text-white">{camera.name}</h2>
        <Link
          href={`/cameras/${camera.id}/edit`}
          className="shrink-0 text-sm text-emerald-400 hover:text-emerald-300"
        >
          Edit
        </Link>
      </div>
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
