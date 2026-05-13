/**
 * API client for ConnorAgent FastAPI backend.
 * TODO: Replace BASE_URL with actual backend URL once FastAPI is set up.
 * TODO: Add auth headers once authentication is implemented.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// TODO: implement when FastAPI /stats endpoint exists
export async function fetchPipelineStats() {
  return apiFetch("/stats");
}

// TODO: implement when FastAPI /contacts endpoint exists
export async function fetchContacts(params?: {
  category?: string;
  role_type?: string;
  is_targeted?: boolean;
  search?: string;
}) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.role_type) qs.set("role_type", params.role_type);
  if (params?.is_targeted !== undefined) qs.set("is_targeted", String(params.is_targeted));
  if (params?.search) qs.set("search", params.search);
  return apiFetch(`/contacts?${qs}`);
}

// TODO: implement when FastAPI /outreach endpoint exists
export async function sendOutreachEmail(payload: {
  contact_id: string;
  subject: string;
  body: string;
}) {
  return apiFetch("/outreach/send", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// TODO: implement when FastAPI /pipeline/run endpoint exists
export async function runPipelineStage(stage: string) {
  return apiFetch(`/pipeline/run/${stage}`, { method: "POST" });
}

// TODO: implement Gmail OAuth flow
export async function getGmailAuthUrl(): Promise<{ url: string }> {
  return apiFetch("/auth/gmail");
}
