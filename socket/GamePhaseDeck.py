import dataclasses
import datetime
import json
import uuid
from configparser import ConfigParser

import psycopg2

from Card import Card
from CardCollection import CardCollection
from Game import Game
from Player import Player
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
    
    def __post_init__(self):
        self.updated_at = self.created_at
    
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


if __name__ == '__main__':
    u = User(name="Alfredo")
    g = Game(current_player=u.id, host=u.id)
    deck = GamePhaseDeck(phase="S", game_id=g.id, deck=CardCollection([Card.from_string("R3"), Card.from_string("B7")]))
    
    assert deck == GamePhaseDeck.fromJSON(deck.toJSON())
    
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
        GamePhaseDeck.set_cursor(cur)

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
            CONSTRAINT players_pk PRIMARY KEY (id),
            CONSTRAINT players_games_fk FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT players_users_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE UNIQUE INDEX players_game_id_turn_index_idx ON players (game_id,turn_index);
        CREATE UNIQUE INDEX players_game_id_user_id_idx ON players (game_id,user_id);
        """)
        cur.execute("""
        CREATE TEMP TABLE gamephasedecks (
            id uuid NOT NULL,
            game_id uuid NOT NULL,
            phase text NOT NULL,
            deck json NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            CONSTRAINT gamephasedecks_pk PRIMARY KEY (id),
            CONSTRAINT gamephasedecks_games_fk FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)
        
        u.save()
        g.save()
        deck.save()
        
        assert deck == GamePhaseDeck.get_by_id(deck.id)
