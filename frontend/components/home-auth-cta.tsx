"use client";

import Link from "next/link";

import { useAuth } from "./auth-provider";

const primaryBtnClass =
  "inline-flex rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500";
const secondaryBtnClass =
  "inline-flex rounded-md border border-slate-600 px-4 py-2 text-sm font-medium text-slate-100 hover:border-slate-500 hover:bg-slate-900";

export function HomeAuthCta() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <p className="text-sm text-slate-500" aria-live="polite">
        Loading…
      </p>
    );
  }

  if (user) {
    return (
      <div className="flex flex-wrap gap-3">
        <Link href="/cameras" className={primaryBtnClass}>
          Go to cameras
        </Link>
        <Link href="/project-status" className={secondaryBtnClass}>
          View project status
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-3">
      <Link href="/register" className={primaryBtnClass}>
        Sign up
      </Link>
      <Link href="/login" className={secondaryBtnClass}>
        Log in
      </Link>
      <Link href="/project-status" className={secondaryBtnClass}>
        View project status
      </Link>
    </div>
  );
}
