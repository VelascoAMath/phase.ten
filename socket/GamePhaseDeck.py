import dataclasses
import datetime
import json
import sqlite3
import uuid
from typing import Self

import psycopg2

from Card import Card
from CardCollection import CardCollection
from Game import Game
from User import User
from add_db_functions import add_db_functions


@dataclasses.dataclass
@add_db_functions(db_name='gamephasedecks', plural_foreign=[('game_id', "games", Game)])
class GamePhaseDeck:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    game_id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    phase: str = ""
    deck: CardCollection = dataclasses.field(default=CardCollection)
    created_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    updated_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    
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
        return GamePhaseDeck.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        
        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)
        
        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)
        
        return GamePhaseDeck(
            uuid.UUID(data["id"]),
            uuid.UUID(data["game_id"]),
            data["phase"],
            CardCollection(Card.fromJSONDict(x) for x in data["deck"]),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    @classmethod
    def set_cursor(cls, cur: sqlite3.Cursor | psycopg2.extensions.cursor):
        pass
    
    @classmethod
    def all_where_game_id(cls, game_id: str | uuid.UUID) -> list[Self]:
        pass
    
    @classmethod
    def get_by_id(cls, id: str | uuid.UUID) -> Self:
        pass
    
    def save(self):
        pass
    
    def delete(self):
        pass


if __name__ == '__main__':
    u = User(name="Alfredo")
    g = Game(current_player=u.id, host=u.id)
    deck = GamePhaseDeck(phase="S", game_id=g.id, deck=CardCollection([Card.from_string("R3"), Card.from_string("B7")]))
    
    assert deck == GamePhaseDeck.fromJSON(deck.toJSON())
