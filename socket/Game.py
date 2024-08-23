import dataclasses
import datetime
import json
import sqlite3
import uuid
from configparser import ConfigParser
import random
from typing import Self

import psycopg2

from Card import Card
from CardCollection import CardCollection
from User import User
from add_db_functions import add_db_functions


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
    
    g = Game(uuid.uuid4(), phase_list, deck, discard_list, alfredo.id, naly.id, True, alfredo.id)
    print(g)
    h = Game.fromJSON(g.toJSON())
    print(h)
    assert g == h
    
    parser = ConfigParser()
    config = {}
    
    parser.read('database.ini')
    if parser.has_section('postgresql'):
        for param in parser.items('postgresql'):
            config[param[0]] = param[1]
    else:
        raise Exception(f"No postgresql section in database.ini!")
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        User.set_cursor(cur)
        Game.set_cursor(cur)
        cur.execute(
            """
            CREATE TEMP TABLE users (
                id uuid NOT NULL,
                name text NOT NULL,
                "token" text NOT NULL,
                created_at timestamp NOT NULL,
                updated_at timestamp NOT NULL,
                CONSTRAINT users_pk PRIMARY KEY (id)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS users_name_idx ON users (name);
            """
        )
        cur.execute("""
        CREATE TEMP TABLE games (
            id uuid NOT NULL,
            phase_list json NOT NULL,
            deck json NOT NULL,
            "discard" json NOT NULL,
            current_player uuid NOT NULL,
            host uuid NOT NULL,
            in_progress boolean DEFAULT false NOT NULL,
            winner uuid NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            CONSTRAINT game_pk PRIMARY KEY (id),
            CONSTRAINT game_users_fk FOREIGN KEY (current_player) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT game_users_fk_1 FOREIGN KEY (host) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT game_users_fk_2 FOREIGN KEY (winner) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)
        
        alfredo.save()
        naly.save()
        cur.execute("SELECT * FROM users")
        g.save()
        assert Game.get_by_id(g.id) == g
    


if __name__ == "__main__":
    main()
