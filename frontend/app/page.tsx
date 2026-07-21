import { HomeAuthCta } from "@/components/home-auth-cta";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold tracking-tight text-white">
        Datachain
      </h1>
      <p className="text-slate-400">
        Decentralized, tamper-evident CCTV video management. Sign up or log in
        to manage your cameras and verify recorded footage.
      </p>
      <HomeAuthCta />
    </div>
  );
}
