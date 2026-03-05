import type { BoardData } from "@/lib/kanban";
import { getAccessToken } from "@/lib/auth";

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

const withAuthHeaders = async (headers?: HeadersInit): Promise<HeadersInit> => {
  const token = await getAccessToken();
  if (!token) {
    return headers ?? {};
  }

  return {
    ...(headers ?? {}),
    Authorization: `Bearer ${token}`,
  };
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
    headers: await withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return (await response.json()) as BoardData;
};

export const saveBoard = async (board: BoardData): Promise<BoardData> => {
  const response = await fetch("/api/board", {
    method: "PUT",
    headers: await withAuthHeaders({
      "Content-Type": "application/json",
    }),
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
    headers: await withAuthHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({ question, history }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return (await response.json()) as AIChatResponse;
};
