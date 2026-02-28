import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AIChatSidebar } from "@/components/AIChatSidebar";

describe("AIChatSidebar", () => {
  it("renders empty state and sends a question", async () => {
    const onSend = vi.fn(async () => undefined);
    render(<AIChatSidebar messages={[]} isLoading={false} onSend={onSend} />);

    await userEvent.type(screen.getByLabelText(/ai question/i), "Suggest a task");
    await userEvent.click(screen.getByRole("button", { name: /ask ai/i }));

    expect(onSend).toHaveBeenCalledWith("Suggest a task");
  });

  it("renders conversation messages", () => {
    render(
      <AIChatSidebar
        isLoading={false}
        onSend={vi.fn(async () => undefined)}
        messages={[
          { role: "user", content: "Hello" },
          { role: "assistant", content: "Hi there" },
        ]}
      />
    );

    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hi there")).toBeInTheDocument();
  });
});
