import dataclasses
import datetime
import json
import random
import sqlite3
import uuid
from enum import Enum
from typing import Self

import psycopg2

from Card import Card
from CardCollection import CardCollection
from User import User
from add_db_functions import add_db_functions


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


@dataclasses.dataclass(order=True)
@add_db_functions(db_name='games', single_foreign=[('current_player', User), ('host', User), ('winner', User)])
class Game:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    phase_list: list[str] = dataclasses.field(default_factory=list)
    deck: CardCollection = dataclasses.field(default_factory=CardCollection)
    discard: CardCollection = dataclasses.field(default_factory=CardCollection)
    current_player: uuid.UUID = None
    # The player who originally created the game
    host: uuid.UUID = None
    # If the game has started
    in_progress: bool = False
    type: GameType = GameType.NORMAL
    winner: uuid.UUID = None
    created_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    updated_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    
    def __post_init__(self):
        self.updated_at = self.created_at
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "phase_list": self.phase_list,
            "deck": [x.to_json_dict() for x in self.deck],
            "discard": [x.to_json_dict() for x in self.discard],
            "current_player": str(self.current_player),
            "host": str(self.host),
            "in_progress": self.in_progress,
            "type": self.type.name,
            "winner": None if self.winner is None else str(self.winner),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
    
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Game.from_json_dict(data)
    
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
        
        return Game(uuid.UUID(data["id"]), data["phase_list"], deck, discard, uuid.UUID(data["current_player"]),
                    uuid.UUID(data["host"]), data["in_progress"],
                    GameType.from_string(data["type"]),
                    None if data["winner"] is None else uuid.UUID(data["winner"]),
                    created_at=created_at, updated_at=updated_at)
    
    @classmethod
    def set_cursor(cls, cur: sqlite3.Cursor | psycopg2.extensions.cursor):
        pass
    
    @classmethod
    def get_by_id(cls, game_id: str | uuid.UUID) -> Self:
        pass
    
    def save(self):
        pass
    
    @classmethod
    def all(cls) -> list[Self]:
        pass
    
    @classmethod
    def exists(cls, game_id: str | uuid.UUID) -> bool:
        pass
    
    def delete(self):
        pass


def main():
    deck = Card.getNewDeck()
    while len(deck) > 10:
        deck.pop()
    
    random.seed(0)
    random.shuffle(deck)
    
    phase_list = [
        "S3+S3",
        "S3+R4",
        "S4+R4",
        "R7",
        "R8",
        "R9",
        "S4+S4",
        "C7",
        "S5+S2",
        "S5+S3",
    ]
    discard_list = CardCollection([deck.pop() for _ in range(5)])
    
    alfredo = User(name="Alfredo")
    naly = User(name="Naly")
    
    g = Game(uuid.uuid4(), phase_list, deck, discard_list, alfredo.id, naly.id, True, GameType.LEGACY, alfredo.id)
    print(g)
    h = Game.fromJSON(g.toJSON())
    print(h)
    assert g == h


if __name__ == "__main__":
    main()
