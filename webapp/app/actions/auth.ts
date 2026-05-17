"use server";

import { createHash, timingSafeEqual } from "crypto";
import { redirect } from "next/navigation";
import { createSession, deleteSession } from "@/lib/session";

function passwordsMatch(input: string, stored: string): boolean {
  const inputHash = createHash("sha256").update(input.trim()).digest();
  const storedHash = createHash("sha256").update(stored.trim()).digest();
  return timingSafeEqual(inputHash, storedHash);
}

export async function login(
  _state: { error?: string } | undefined,
  formData: FormData
) {
  const password = (formData.get("password") as string) ?? "";
  const adminPassword = process.env.ADMIN_PASSWORD;

  if (!adminPassword?.trim()) {
    console.error("ADMIN_PASSWORD is missing or empty for this deployment.");
    return { error: "Login is not configured. Check ADMIN_PASSWORD in Vercel." };
  }

  if (!passwordsMatch(password, adminPassword)) {
    return { error: "Invalid password" };
  }

  await createSession();
  redirect("/dashboard");
}

export async function logout() {
  await deleteSession();
  redirect("/login");
}
