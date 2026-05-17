import { describe, expect, it } from "vitest";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./tokenStorage";

describe("tokenStorage", () => {
  it("stores and clears access/refresh token pair", () => {
    setTokens("access", "refresh");

    expect(getAccessToken()).toBe("access");
    expect(getRefreshToken()).toBe("refresh");

    clearTokens();

    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });
});
