export default function ProjectStatusPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-white">Project status</h1>
      <p className="text-slate-400">
        Epic 1 is in progress: this page demonstrates{" "}
        <span className="font-mono text-slate-300">App Router</span> routing
        with a kebab-case URL segment (
        <span className="font-mono text-slate-300">/project-status</span>).
      </p>
      <ul className="list-inside list-disc space-y-2 text-slate-400">
        <li>Frontend dev server: see README in this folder.</li>
        <li>Backend health: FastAPI GET /health (when API is running).</li>
        <li>Database: Docker Compose PostgreSQL at repo root.</li>
      </ul>
    </div>
  );
}
