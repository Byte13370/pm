import {
  getAccessToken,
  signInWithPassword,
  signOut,
  signUpWithPassword,
} from "@/lib/auth";

const { getSession, signInWithPasswordMock, signUpMock, signOutMock } = vi.hoisted(() => ({
  getSession: vi.fn(),
  signInWithPasswordMock: vi.fn(),
  signUpMock: vi.fn(),
  signOutMock: vi.fn(),
}));

vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession,
      signInWithPassword: signInWithPasswordMock,
      signUp: signUpMock,
      signOut: signOutMock,
    },
  },
}));

describe("auth helpers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("reads access token from current session", async () => {
    getSession.mockResolvedValue({
      data: { session: { access_token: "token-123" } },
    });

    await expect(getAccessToken()).resolves.toBe("token-123");
  });

  it("signs in with email/password", async () => {
    signInWithPasswordMock.mockResolvedValue({ error: null });

    await expect(signInWithPassword("user@example.com", "password123")).resolves.toBeUndefined();
    expect(signInWithPasswordMock).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "password123",
    });
  });

  it("returns confirmation requirement when signup has no session", async () => {
    signUpMock.mockResolvedValue({ data: { session: null }, error: null });

    await expect(signUpWithPassword("new@example.com", "password123")).resolves.toEqual({
      requiresEmailConfirmation: true,
    });
  });

  it("signs out current session", async () => {
    signOutMock.mockResolvedValue({ error: null });

    await expect(signOut()).resolves.toBeUndefined();
  });
});
