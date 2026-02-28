"use client";

import { FormEvent, useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type AIChatSidebarProps = {
  messages: ChatMessage[];
  isLoading: boolean;
  onSend: (question: string) => Promise<void>;
};

export const AIChatSidebar = ({ messages, isLoading, onSend }: AIChatSidebarProps) => {
  const [question, setQuestion] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmed = question.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setQuestion("");
    await onSend(trimmed);
  };

  return (
    <aside className="flex h-full flex-col rounded-3xl border border-[var(--stroke)] bg-white p-5 shadow-[var(--shadow)]">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--gray-text)]">
          AI Assistant
        </p>
        <h2 className="mt-2 font-display text-xl font-semibold text-[var(--navy-dark)]">
          Kanban Chat
        </h2>
      </div>

      <div className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1" data-testid="ai-chat-messages">
        {messages.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-[var(--stroke)] px-3 py-3 text-sm text-[var(--gray-text)]">
            Ask the AI to suggest, create, move, or edit cards.
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`rounded-2xl px-3 py-3 text-sm leading-6 ${
                message.role === "user"
                  ? "ml-6 border border-[var(--stroke)] bg-[var(--surface)] text-[var(--navy-dark)]"
                  : "mr-6 border border-[var(--stroke)] bg-white text-[var(--gray-text)]"
              }`}
            >
              <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--gray-text)]">
                {message.role === "user" ? "You" : "Assistant"}
              </p>
              <p>{message.content}</p>
            </div>
          ))
        )}
      </div>

      <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
        <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
          Message
        </label>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={3}
          placeholder="Ask the assistant..."
          className="w-full resize-none rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
          aria-label="AI question"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-white transition enabled:hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isLoading ? "Thinking..." : "Ask AI"}
        </button>
      </form>
    </aside>
  );
};
