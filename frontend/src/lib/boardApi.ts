import type { BoardData } from "@/lib/kanban";

export type ConversationMessage = {
  role: "user" | "assistant";
  content: string;
};

export type AIChatResponse = {
  model: string;
  assistant_response: string;
  board_updated: boolean;
  board: BoardData;
};

const getErrorMessage = async (response: Response) => {
  try {
    const payload = await response.json();
    if (payload?.detail) {
      return String(payload.detail);
    }
  } catch {
    return response.statusText || "Request failed";
  }

  return response.statusText || "Request failed";
};

export const fetchBoard = async (): Promise<BoardData> => {
  const response = await fetch("/api/board", {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return (await response.json()) as BoardData;
};

export const saveBoard = async (board: BoardData): Promise<BoardData> => {
  const response = await fetch("/api/board", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(board),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return (await response.json()) as BoardData;
};

export const sendAIChat = async (
  question: string,
  history: ConversationMessage[]
): Promise<AIChatResponse> => {
  const response = await fetch("/api/ai/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ question, history }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return (await response.json()) as AIChatResponse;
};
