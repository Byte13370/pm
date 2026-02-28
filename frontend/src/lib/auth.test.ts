import {
  AUTH_COOKIE_NAME,
  AUTH_COOKIE_VALUE,
  buildAuthCookie,
  buildClearAuthCookie,
  hasAuthCookie,
  validateCredentials,
} from "@/lib/auth";

describe("auth helpers", () => {
  it("accepts dummy credentials", () => {
    expect(validateCredentials("user", "password")).toBe(true);
  });

  it("rejects invalid credentials", () => {
    expect(validateCredentials("wrong", "password")).toBe(false);
    expect(validateCredentials("user", "wrong")).toBe(false);
  });

  it("detects auth cookie", () => {
    const cookie = `${AUTH_COOKIE_NAME}=${AUTH_COOKIE_VALUE}; other=value`;
    expect(hasAuthCookie(cookie)).toBe(true);
    expect(hasAuthCookie("other=value")).toBe(false);
  });

  it("builds auth and clear cookie values", () => {
    expect(buildAuthCookie()).toContain(`${AUTH_COOKIE_NAME}=${AUTH_COOKIE_VALUE}`);
    expect(buildClearAuthCookie()).toContain(`${AUTH_COOKIE_NAME}=`);
    expect(buildClearAuthCookie()).toContain("Max-Age=0");
  });
});
