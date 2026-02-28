from typing import Literal

from pydantic import BaseModel, model_validator


class Card(BaseModel):
    id: str
    title: str
    details: str


class Column(BaseModel):
    id: str
    title: str
    cardIds: list[str]


class BoardData(BaseModel):
    columns: list[Column]
    cards: dict[str, Card]

    @model_validator(mode="after")
    def validate_board_consistency(self) -> "BoardData":
        card_keys = set(self.cards.keys())

        for key, card in self.cards.items():
            if card.id != key:
                raise ValueError(f"Card id mismatch: key '{key}' != card.id '{card.id}'")

        referenced_ids: list[str] = []
        for column in self.columns:
            referenced_ids.extend(column.cardIds)

        missing_card_ids = sorted({card_id for card_id in referenced_ids if card_id not in card_keys})
        if missing_card_ids:
            raise ValueError(f"Missing cards referenced by columns: {', '.join(missing_card_ids)}")

        return self


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AIChatRequest(BaseModel):
    question: str
    history: list[ConversationMessage] = []


class AIStructuredOutput(BaseModel):
    assistant_response: str
    board_update: BoardData | None = None


class AIChatResponse(BaseModel):
    model: str
    assistant_response: str
    board_updated: bool
    board: BoardData
