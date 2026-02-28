import { fetchBoard, saveBoard, sendAIChat } from "@/lib/boardApi";
import { initialData } from "@/lib/kanban";

describe("boardApi", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches board data", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify(initialData), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      )
    );

    const board = await fetchBoard();
    expect(board.columns).toHaveLength(5);
  });

  it("saves board data", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: RequestInfo | URL, init?: RequestInit) =>
        new Response(String(init?.body), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      )
    );

    const updated = await saveBoard(initialData);
    expect(updated.columns[0].id).toBe(initialData.columns[0].id);
  });

  it("throws when fetch fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ detail: "Authentication required" }), {
          status: 401,
          headers: { "Content-Type": "application/json" },
        })
      )
    );

    await expect(fetchBoard()).rejects.toThrow("Authentication required");
  });

  it("sends ai chat and receives structured response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(
          JSON.stringify({
            model: "test-model",
            assistant_response: "Done",
            board_updated: true,
            board: initialData,
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }
        )
      )
    );

    const result = await sendAIChat("Update board", []);
    expect(result.assistant_response).toBe("Done");
    expect(result.board_updated).toBe(true);
  });
});
