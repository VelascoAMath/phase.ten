import dataclasses
import datetime
import json
import uuid

import peewee

from BaseModel import BaseModel, CardListField
from Card import Card
from CardCollection import CardCollection
from Games import Games


@dataclasses.dataclass(init=False)
class Gamephasedecks(BaseModel):
    game: Games = peewee.ForeignKeyField(
        column_name="game_id", field="id", model=Games, null=False
    )
    phase: str = peewee.TextField(null=False)
    deck: CardCollection = CardListField(null=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def toJSON(self):
        return json.dumps(self.to_json_dict())

    def to_json_dict(self):
        return {
            "id": str(self.id),
            "game_id": str(self.game_id),
            "phase": self.phase,
            "deck": self.deck.to_json_dict(),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Gamephasedecks.from_json_dict(data)

    @staticmethod
    def from_json_dict(data):
        created_at = data["created_at"]
        updated_at = data["updated_at"]

        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)

        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)

        return Gamephasedecks(
            id=uuid.UUID(data["id"]),
            game=uuid.UUID(data["game_id"]),
            phase=data["phase"],
            deck=CardCollection(Card.fromJSONDict(x) for x in data["deck"]),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self):
        return f"Gamephasedecks(id={self.id}, game_id={self.game.id}, phase={self.phase}, deck={self.deck}, created_at={self.created_at}, updated_at={self.updated_at})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Gamephasedecks):
            return (
                self.id == other.id
                and self.game == other.game
                and self.phase == other.phase
                and self.deck == other.deck
                and self.created_at == other.created_at
                and self.updated_at == other.created_at
            )
        else:
            return False

    class Meta:
        table_name = "gamephasedecks"
