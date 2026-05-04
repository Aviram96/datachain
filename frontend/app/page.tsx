import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold tracking-tight text-white">
        Datachain
      </h1>
      <p className="text-slate-400">
        Decentralized, tamper-evident CCTV video management. This is the Epic 1
        frontend scaffold: Next.js, Tailwind, routing, ESLint, and Prettier.
      </p>
      <Link
        href="/project-status"
        className="inline-flex rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
      >
        View project status
      </Link>
    </div>
  );
}
