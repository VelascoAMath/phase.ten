import dataclasses
import datetime
import json
import sqlite3
import uuid
from configparser import ConfigParser
from typing import Self

import psycopg2

from Card import Card
from CardCollection import CardCollection
from Game import Game
from User import User
from add_db_functions import add_db_functions


@dataclasses.dataclass(order=True)
@add_db_functions(db_name='players', single_foreign=[('game_id', Game), ('user_id', User)],
                  unique_indices=[['game_id', 'turn_index'], ['game_id', 'user_id']], serial_set={'turn_index'})
class Player:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    game_id: uuid.UUID = None
    user_id: uuid.UUID = None
    hand: CardCollection = dataclasses.field(default_factory=CardCollection)
    # Does this player go first, second, etc
    turn_index: int = -1
    phase_index: int = 0
    drew_card: bool = False
    completed_phase: bool = False
    skip_cards: CardCollection = dataclasses.field(default_factory=CardCollection)
    created_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    updated_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    
    def __post_init__(self):
        self.updated_at = self.created_at
    
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "game_id": str(self.game_id),
            "user_id": str(self.user_id),
            "hand": self.hand.to_json_dict(),
            "turn_index": self.turn_index,
            "phase_index": self.phase_index,
            "drew_card": self.drew_card,
            "completed_phase": self.completed_phase,
            "skip_cards": self.skip_cards.to_json_dict(),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Player.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        
        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)
        
        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)
        
        return Player(
            uuid.UUID(data["id"]),
            uuid.UUID(data["game_id"]),
            uuid.UUID(data["user_id"]),
            CardCollection(Card.fromJSONDict(card) for card in data["hand"]),
            data["turn_index"],
            data["phase_index"],
            data["drew_card"],
            data["completed_phase"],
            CardCollection(Card.fromJSONDict(card) for card in data["skip_cards"]),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    @classmethod
    def exists(cls, player_id: str | uuid.UUID) -> bool:
        pass
    
    @classmethod
    def set_cursor(cls, cur: sqlite3.Cursor | psycopg2.extensions.cursor):
        pass
    
    @classmethod
    def all(cls) -> list[Self]:
        pass
    
    def save(self):
        pass
    
    @classmethod
    def get_by_id(cls, player_id: str | uuid.UUID) -> Self:
        pass
    
    @classmethod
    def get_by_game_id_user_id(cls, game_id: str | uuid.UUID, to_id: str | uuid.UUID) -> Self:
        pass
    
    @classmethod
    def exists_by_game_id_user_id(cls, game_id: str | uuid.UUID, user_id: str | uuid.UUID) -> bool:
        pass
    
    def delete(self):
        pass


def main():
    u = User(name="Alfredo")
    g = Game(id=uuid.uuid4(), current_player=u.id, host=u.id)
    p = Player(
        id=uuid.uuid4(),
        game_id=g.id,
        user_id=u.id,
        hand=CardCollection([
            Card.from_string("R10"),
            Card.from_string("W"),
            Card.from_string("S"),
            Card.from_string("B4"),
        ]),
        turn_index=4,
        phase_index=8,
        drew_card=True,
        completed_phase=True,
        skip_cards=CardCollection([Card.from_string("S"), Card.from_string("S"), Card.from_string("S")])
    )
    
    print(p)
    print(p.toJSON())
    print(Player.fromJSON(p.toJSON()))
    assert p == Player.fromJSON(p.toJSON())
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
        Player.set_cursor(cur)
        
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
        cur.execute("""
        CREATE TEMP TABLE players (
            id uuid NOT NULL,
            game_id uuid NOT NULL,
            user_id uuid NOT NULL,
            hand json NOT NULL,
            turn_index serial NOT NULL,
            phase_index int NOT NULL,
            drew_card boolean DEFAULT false NOT NULL,
            completed_phase boolean DEFAULT false NOT NULL,
            skip_cards json NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            CONSTRAINT players_pk PRIMARY KEY (id),
            CONSTRAINT players_games_fk FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT players_users_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE UNIQUE INDEX players_game_id_turn_index_idx ON players (game_id,turn_index);
        CREATE UNIQUE INDEX players_game_id_user_id_idx ON players (game_id,user_id);
        """)
        
        u.save()
        g.save()
        p.save()


if __name__ == "__main__":
    main()
