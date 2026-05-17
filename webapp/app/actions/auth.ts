"use server";

import { createHash, timingSafeEqual } from "crypto";
import { redirect } from "next/navigation";
import { createSession, deleteSession } from "@/lib/session";

function passwordsMatch(input: string, stored: string): boolean {
  const a = createHash("sha256").update(input).digest();
  const b = createHash("sha256").update(stored).digest();
  return timingSafeEqual(a, b);
}

export async function login(
  _state: { error?: string } | undefined,
  formData: FormData
) {
  const password = (formData.get("password") as string) ?? "";
  const adminPassword = process.env.ADMIN_PASSWORD ?? "";

  if (!adminPassword || !passwordsMatch(password, adminPassword)) {
    return { error: "Invalid password" };
  }

  await createSession();
  redirect("/dashboard");
}

export async function logout() {
  await deleteSession();
  redirect("/login");
}
