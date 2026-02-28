import json
from typing import Any

from app.ai import ask_openrouter_messages
from app.schemas import AIStructuredOutput, BoardData, ConversationMessage


SYSTEM_PROMPT = (
    "You are a project-management assistant. "
    "Always return valid JSON only, no markdown and no extra keys. "
    "The JSON schema is: "
    "{\"assistant_response\": string, \"board_update\": BoardData|null}."
)


def _extract_json_payload(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[-1].strip().startswith("```"):
            text = "\n".join(lines[1:-1]).strip()
            if text.startswith("json"):
                text = text[4:].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError("Model did not return valid JSON")

        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Model returned malformed JSON") from exc


def build_structured_messages(
    question: str,
    board: BoardData,
    history: list[ConversationMessage],
) -> list[dict[str, str]]:
    board_json = json.dumps(board.model_dump(), ensure_ascii=False)
    history_json = json.dumps([message.model_dump() for message in history], ensure_ascii=False)

    user_prompt = (
        "Current board JSON:\n"
        f"{board_json}\n\n"
        "Conversation history JSON:\n"
        f"{history_json}\n\n"
        "User question:\n"
        f"{question}\n\n"
        "Return only strict JSON matching the schema."
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def run_structured_board_assistant(
    question: str,
    board: BoardData,
    history: list[ConversationMessage],
) -> tuple[AIStructuredOutput, str]:
    messages = build_structured_messages(question=question, board=board, history=history)
    raw_response, model = ask_openrouter_messages(messages)
    payload = _extract_json_payload(raw_response)

    try:
        structured = AIStructuredOutput.model_validate(payload)
    except Exception as exc:
        raise RuntimeError(f"Model output did not match schema: {exc}") from exc

    return structured, model
