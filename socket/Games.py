import dataclasses
import datetime
import json
import uuid
from enum import Enum
from typing import Any

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
    field_type = "game_type"
    
    def db_value(self, value: GameType) -> str:
        return value.name
    
    def python_value(self, value: str) -> GameType:
        return GameType.from_string(value)


class TimeIntervalField(peewee.Field):
    field_type = "interval"
    
    def db_value(self, value: datetime.timedelta) -> str:
        return f"{value.total_seconds()} seconds"


class DateTimeZField(peewee.Field):
    field_type = "timestamptz"
    
    def db_value(self, value: datetime.datetime) -> str:
        return str(value)
    

@dataclasses.dataclass(init=False)
class Games(BaseModel):
    phase_list: list[str] = StringListField(null=False)
    deck: CardCollection = CardListField(null=False)
    discard: CardCollection = CardListField(null=False)
    current_player: Users = peewee.ForeignKeyField(
        column_name="current_player", field="id", model=Users, null=False
    )
    # The player who originally created the game
    host: Users = peewee.ForeignKeyField(
        backref="users_host_set",
        column_name="host",
        field="id",
        model=Users,
        null=False,
    )
    # If the game has started
    in_progress: bool = peewee.BooleanField(default=False, null=False)
    type: GameType = GameTypeField(default=GameType.NORMAL, null=False)
    winner: Users | None = peewee.ForeignKeyField(
        backref="users_winner_set",
        column_name="winner",
        field="id",
        model=Users,
        null=True,
    )
    last_move_made: datetime.datetime = DateTimeZField(
        null=False, default=lambda: datetime.datetime.now(tz=datetime.timezone.utc)
    )
    player_time_limit: datetime.timedelta = TimeIntervalField(
        null=False, default=datetime.timedelta(minutes=2)
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
            "last_move_made": str(self.last_move_made),
            "player_time_limit": (
                self.player_time_limit.days, self.player_time_limit.seconds, self.player_time_limit.microseconds),
            "next_player_alarm": str(self.last_move_made + self.player_time_limit),
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
            last_move_made=datetime.datetime.fromisoformat(data["last_move_made"]),
            player_time_limit=datetime.timedelta(days=data["player_time_limit"][0],
                                                 seconds=data["player_time_limit"][1],
                                                 microseconds=data["player_time_limit"][2]),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def __repr__(self):
        return (
            f"Games(id={self.id}, phase_list={self.phase_list}, deck={self.deck}, discard={self.discard}, "
            f"current_player={self.current_player}, host={self.host}, type={self.type}, winner={self.winner}, "
            f"created_at={self.created_at}, updated_at={self.updated_at}), last_move_made={self.last_move_made}, "
            f"player_time_limit={self.player_time_limit})"
        )
    
    def __str__(self):
        return self.__repr__()
    
    def __eq__(self, other):
        if isinstance(other, Games):
            return (
                super().__eq__(other)
                and self.phase_list == other.phase_list
                and self.deck == other.deck
                and self.discard == other.discard
                and self.current_player == other.current_player
                and self.host == other.host
                and self.type == other.type
                and self.winner == other.winner
                and self.last_move_made == other.last_move_made
                and self.player_time_limit == other.player_time_limit
            )
        else:
            return False
    
    class Meta:
        table_name = "games"
    
    @classmethod
    def exists(cls, game_id: Any):
        return Games.get_or_none(id=game_id) is not None


def main():
    u = Users.get_or_none(Users.name == "Who cares?")
    if u is None:
        u = Users(name="Who cares?")
        u.save(force_insert=True)
    
    g = Games(
        current_player=u,
        host=u,
        phase_list=["S3+S3"],
        deck=CardCollection(CardCollection.getNewDeck()[0:1]),
        discard=CardCollection(),
        player_time_limit=datetime.timedelta(minutes=5),
    )
    g.save(force_insert=True)
    g: Games = Games.get_by_id(g.id)
    print(g)
    print(Games.fromJSON(g.toJSON()))
    assert g == Games.fromJSON(g.toJSON())
    g.delete_instance()
    u.delete_instance()


if __name__ == "__main__":
    main()
