"use client";

import Link from "next/link";

import { useAuth } from "./auth-provider";

export function SiteHeader() {
  const { user, isLoading, logout } = useAuth();

  return (
    <header className="border-b border-landing-ink/10 bg-white/70 backdrop-blur-md">
      <nav className="mx-auto flex max-w-3xl flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3.5 text-sm font-medium sm:px-6">
        <Link
          href={user ? "/cameras" : "/"}
          className="font-display text-base font-semibold tracking-tight text-landing-ink hover:text-landing-accent"
        >
          Datachain
        </Link>
        {isLoading ? null : user ? (
          <>
            <Link
              href="/cameras"
              className="text-landing-ink/65 transition hover:text-landing-ink"
            >
              Cameras
            </Link>
            <Link
              href="/cameras/new"
              className="text-landing-ink/65 transition hover:text-landing-ink"
            >
              Add camera
            </Link>
            <span
              className="text-landing-ink/55"
              title={user.email}
            >
              Signed in as{" "}
              <span className="font-medium text-landing-ink">{user.email}</span>
            </span>
            <button
              type="button"
              onClick={logout}
              className="text-landing-ink/65 transition hover:text-landing-ink"
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="text-landing-ink/65 transition hover:text-landing-ink"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-md bg-landing-accent px-3 py-1.5 font-semibold text-white transition hover:bg-landing-accent-soft"
            >
              Sign up
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
