"use client";

import { FormEvent, useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import {
  getAccessToken,
  signInWithPassword,
  signOut,
  signUpWithPassword,
} from "@/lib/auth";

export const AuthGate = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadSession = async () => {
      try {
        const token = await getAccessToken();
        if (!isMounted) {
          return;
        }
        setIsAuthenticated(Boolean(token));
      } catch {
        if (!isMounted) {
          return;
        }
        setIsAuthenticated(false);
      } finally {
        if (isMounted) {
          setIsAuthLoading(false);
        }
      }
    };

    void loadSession();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setInfo("");

    try {
      if (mode === "signup") {
        const result = await signUpWithPassword(email, password);
        if (result.requiresEmailConfirmation) {
          setInfo("Signup succeeded. Confirm your email, then sign in.");
          setPassword("");
          return;
        }

        setIsAuthenticated(true);
        setPassword("");
        return;
      }

      await signInWithPassword(email, password);
      setIsAuthenticated(true);
      setPassword("");
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Authentication failed.";
      setError(message);
    }
  };

  const handleLogout = async () => {
    await signOut();
    setIsAuthenticated(false);
    setEmail("");
    setPassword("");
    setError("");
    setInfo("");
  };

  if (isAuthLoading) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center justify-center px-6">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
          Checking session...
        </p>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
        <section className="w-full rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
            Project Management MVP
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
            {mode === "signin" ? "Sign in" : "Sign up"}
          </h1>
          <p className="mt-2 text-sm text-[var(--gray-text)]">
            Use your email and password.
          </p>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                className="w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                aria-label="Email"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                className="w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                aria-label="Password"
                required
              />
            </div>

            {info ? (
              <p className="text-sm font-semibold text-[var(--primary-blue)]" role="status">
                {info}
              </p>
            ) : null}

            {error ? (
              <p className="text-sm font-semibold text-[var(--secondary-purple)]" role="alert">
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:brightness-110"
            >
              {mode === "signin" ? "Sign in" : "Sign up"}
            </button>

            <button
              type="button"
              onClick={() => {
                setMode((previous) => (previous === "signin" ? "signup" : "signin"));
                setError("");
                setInfo("");
              }}
              className="w-full rounded-full border border-[var(--stroke)] px-4 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-[var(--gray-text)] transition hover:text-[var(--navy-dark)]"
            >
              {mode === "signin" ? "Need an account? Sign up" : "Have an account? Sign in"}
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <div>
      <div className="mx-auto flex max-w-[1500px] justify-end px-6 pt-6">
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--gray-text)] transition hover:text-[var(--navy-dark)]"
        >
          Log out
        </button>
      </div>
      <KanbanBoard />
    </div>
  );
};
