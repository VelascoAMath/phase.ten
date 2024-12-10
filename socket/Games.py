import dataclasses
import datetime
import json
import uuid
from enum import Enum

import peewee

from BaseModel import BaseModel, StringListField, CardListField
from Card import Card
from CardCollection import CardCollection
from Users import Users


class GameType(Enum):
    NORMAL = 1
    LEGACY = 2
    ADVANCEMENT = 3
    
    @staticmethod
    def from_string(data):
        match data:
            case "NORMAL":
                return GameType.NORMAL
            case "LEGACY":
                return GameType.LEGACY
            case "ADVANCEMENT":
                return GameType.ADVANCEMENT
            case _:
                raise Exception(f"{data} is not a valid GameType!")


class GameTypeField(peewee.Field):
    field_type = 'game_type'
    
    def db_value(self, value: GameType) -> str:
        return value.name
    
    def python_value(self, value: str) -> GameType:
        return GameType.from_string(value)


@dataclasses.dataclass(init=False)
class Games(BaseModel):
    phase_list = StringListField(null=False)
    deck = CardListField(null=False)
    discard = CardListField(null=False)
    current_player = peewee.ForeignKeyField(
        column_name="current_player", field="id", model=Users, null=False
    )
    # The player who originally created the game
    host = peewee.ForeignKeyField(
        backref="users_host_set",
        column_name="host",
        field="id",
        model=Users,
        null=False,
    )
    # If the game has started
    in_progress = peewee.BooleanField(default=False, null=False)
    type = GameTypeField(default=GameType.NORMAL, null=False)
    winner = peewee.ForeignKeyField(
        backref="users_winner_set",
        column_name="winner",
        field="id",
        model=Users,
        null=True,
    )
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "phase_list": self.phase_list,
            "deck": [x.to_json_dict() for x in self.deck],
            "discard": [x.to_json_dict() for x in self.discard],
            "current_player": str(self.current_player.id),
            "host": str(self.host.id),
            "in_progress": self.in_progress,
            "type": self.type.name,
            "winner": None if self.winner is None else str(self.winner.id),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
    
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Games.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        deck = CardCollection()
        for c in data["deck"]:
            deck.append(Card.fromJSONDict(c))
        discard = CardCollection()
        for c in data["discard"]:
            discard.append(Card.fromJSONDict(c))
        
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        
        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)
        
        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)
        
        return Games(
            id=uuid.UUID(data["id"]),
            phase_list=data["phase_list"],
            deck=deck,
            discard=discard,
            current_player=uuid.UUID(data["current_player"]),
            host=uuid.UUID(data["host"]),
            in_progress=data["in_progress"],
            type=GameType.from_string(data["type"]),
            winner=None if data["winner"] is None else uuid.UUID(data["winner"]),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def __repr__(self):
        return (f"Games(id={self.id}, phase_list={self.phase_list}, deck={self.deck}, discard={self.discard}, "
                f"current_player={self.current_player}, host={self.host}, type={self.type}, winner={self.winner}, "
                f"created_at={self.created_at}, updated_at={self.updated_at})")
    
    def __str__(self):
        return self.__repr__()
    
    def __eq__(self, other):
        if isinstance(other, Games):
            return super().__eq__(
                other) and self.phase_list == other.phase_list and self.deck == other.deck and self.discard == other.discard and self.current_player == other.current_player and self.host == other.host and self.type == other.type and self.winner == other.winner
        else:
            return False
    
    class Meta:
        table_name = "games"
