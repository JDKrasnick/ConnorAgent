import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";

function getSessionKey() {
  const secret = process.env.SESSION_SECRET?.trim();

  if (!secret) {
    throw new Error("SESSION_SECRET is missing or empty for this deployment.");
  }

  return new TextEncoder().encode(secret);
}

export async function encrypt(payload: {
  isAdmin: boolean;
  expiresAt: Date;
}) {
  return new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(getSessionKey());
}

export async function decrypt(session: string | undefined = "") {
  try {
    const { payload } = await jwtVerify(session, getSessionKey(), {
      algorithms: ["HS256"],
    });
    return payload;
  } catch {
    return null;
  }
}

export async function createSession() {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  const session = await encrypt({ isAdmin: true, expiresAt });
  const cookieStore = await cookies();

  cookieStore.set("session", session, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    expires: expiresAt,
    sameSite: "lax",
    path: "/",
  });
}

export async function deleteSession() {
  const cookieStore = await cookies();
  cookieStore.delete("session");
}
