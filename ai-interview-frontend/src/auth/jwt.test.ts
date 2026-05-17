import { describe, expect, it, vi } from "vitest";
import { getJwtPayload, isJwtExpired } from "./jwt";

function makeToken(payload: object) {
  const encoded = btoa(JSON.stringify(payload)).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
  return `header.${encoded}.signature`;
}

describe("jwt helpers", () => {
  it("decodes payload from jwt-like token", () => {
    const token = makeToken({ sub: "user-1", email: "test@example.com" });

    expect(getJwtPayload(token)).toMatchObject({ sub: "user-1", email: "test@example.com" });
  });

  it("detects expired token", () => {
    vi.setSystemTime(new Date("2026-05-12T12:00:00Z"));
    const expired = makeToken({ exp: Math.floor(new Date("2026-05-12T11:59:00Z").getTime() / 1000) });

    expect(isJwtExpired(expired)).toBe(true);

    vi.useRealTimers();
  });
});
