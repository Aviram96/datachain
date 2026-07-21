"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { networkErrorMessage } from "@/lib/api";
import { AuthApiError, login, register } from "@/lib/auth-api";
import { setAccessToken } from "@/lib/auth-token";
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  PASSWORD_REQUIREMENTS_HINT,
  passwordRequirementsError,
} from "@/lib/password-requirements";

import { useAuth } from "./auth-provider";
import { useToast } from "./toast-provider";

export function RegisterForm() {
  const router = useRouter();
  const { refreshSession } = useAuth();
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const requirementError = passwordRequirementsError(password);
    if (requirementError) {
      showToast(requirementError, "error");
      return;
    }

    setSubmitting(true);

    try {
      await register({ email, password });
      const token = await login({ email, password });
      setAccessToken(token.access_token);
      await refreshSession();
      showToast("Registration successful. Welcome to Datachain.", "success");
      router.push("/cameras");
    } catch (error) {
      if (error instanceof AuthApiError && error.status === 409) {
        showToast(error.message, "error");
      } else if (error instanceof AuthApiError) {
        showToast(error.message, "error");
      } else {
        showToast(networkErrorMessage(), "error");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <div className="space-y-1">
        <label htmlFor="email" className="block text-sm text-slate-300">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-emerald-500/50 focus:ring-2"
        />
      </div>
      <div className="space-y-1">
        <label htmlFor="password" className="block text-sm text-slate-300">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={PASSWORD_MIN_LENGTH}
          maxLength={PASSWORD_MAX_LENGTH}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-describedby="password-requirements"
          className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-emerald-500/50 focus:ring-2"
        />
        <p id="password-requirements" className="text-xs text-slate-500">
          {PASSWORD_REQUIREMENTS_HINT}
        </p>
      </div>
      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-60"
      >
        {submitting ? "Creating account…" : "Sign up"}
      </button>
      <p className="text-center text-sm text-slate-400">
        Already have an account?{" "}
        <Link href="/login" className="text-emerald-400 hover:text-emerald-300">
          Log in
        </Link>
      </p>
    </form>
  );
}
