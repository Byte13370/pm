import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthGate } from "@/components/AuthGate";

const { getAccessToken, signInWithPassword, signUpWithPassword, signOut } = vi.hoisted(() => ({
  getAccessToken: vi.fn(),
  signInWithPassword: vi.fn(),
  signUpWithPassword: vi.fn(),
  signOut: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken,
  signInWithPassword,
  signUpWithPassword,
  signOut,
}));

vi.mock("@/components/KanbanBoard", () => ({
  KanbanBoard: () => <div>Kanban board content</div>,
}));

describe("AuthGate", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue(null);
    signInWithPassword.mockResolvedValue(undefined);
    signUpWithPassword.mockResolvedValue({ requiresEmailConfirmation: false });
    signOut.mockResolvedValue(undefined);
  });

  it("shows login form when unauthenticated", async () => {
    render(<AuthGate />);
    expect(await screen.findByRole("heading", { name: /sign in/i })).toBeInTheDocument();
  });

  it("logs in with valid credentials", async () => {
    render(<AuthGate />);

    await userEvent.type(await screen.findByLabelText(/email/i), "user@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/kanban board content/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log out/i })).toBeInTheDocument();
  });

  it("shows error when sign-in fails", async () => {
    signInWithPassword.mockRejectedValue(new Error("Invalid login credentials"));

    render(<AuthGate />);

    await userEvent.type(await screen.findByLabelText(/email/i), "user@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "invalid");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/invalid login credentials/i);
  });

  it("logs out after login", async () => {
    render(<AuthGate />);

    await userEvent.type(await screen.findByLabelText(/email/i), "user@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await userEvent.click(await screen.findByRole("button", { name: /log out/i }));

    expect(signOut).toHaveBeenCalledTimes(1);
    expect(await screen.findByRole("heading", { name: /sign in/i })).toBeInTheDocument();
  });

  it("supports signup mode", async () => {
    render(<AuthGate />);

    await userEvent.click(await screen.findByRole("button", { name: /need an account\? sign up/i }));
    await userEvent.type(screen.getByLabelText(/email/i), "new@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "password123");
    await userEvent.click(screen.getByRole("button", { name: /^sign up$/i }));

    expect(signUpWithPassword).toHaveBeenCalledWith("new@example.com", "password123");
  });
});
