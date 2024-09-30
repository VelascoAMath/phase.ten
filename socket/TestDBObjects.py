import unittest
import uuid
from configparser import ConfigParser
import random

import psycopg2

from Card import Card
from CardCollection import CardCollection
from Game import Game, GameType
from GamePhaseDeck import GamePhaseDeck
from Player import Player
from RE import RE
from User import User


class TestRE(unittest.TestCase):
    
    def setUp(self):
        parser = ConfigParser()
        config = {}
        
        parser.read('database.ini')
        if parser.has_section('postgresql'):
            for param in parser.items('postgresql'):
                config[param[0]] = param[1]
        else:
            raise Exception(f"No postgresql section in database.ini!")
        
        self.conn = psycopg2.connect(**config)
        self.cur = self.conn.cursor()
        User.set_cursor(self.cur)
        Game.set_cursor(self.cur)
        Player.set_cursor(self.cur)
        GamePhaseDeck.set_cursor(self.cur)
        
        self.cur.execute(
            """
            CREATE TEMP TABLE users (
                id uuid NOT NULL,
                name text NOT NULL,
                "token" text NOT NULL,
                is_bot boolean DEFAULT false NOT NULL,
                created_at timestamp NOT NULL,
                updated_at timestamp NOT NULL,
                CONSTRAINT users_pk PRIMARY KEY (id)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS users_name_isbot_idx ON public.users ("name",is_bot);
            CREATE INDEX IF NOT EXISTS users_name_idx ON public.users ("name");
            """
        )
        self.cur.execute("""
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
        self.cur.execute("""
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
        self.cur.execute("""
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
    
    def tearDown(self):
        self.conn.close()
    
    def test_objects(self):
        alfredo = User(
            uuid.uuid4(),
            "Alfredo",
            "secret token",
            is_bot=False,
        )
        assert alfredo == User.fromJSON(alfredo.toJSON())
        
        alfredo = User(name="Alfredo")
        alfredo.save()
        
        u2 = User.get_by_id(alfredo.id)
        assert alfredo == u2
        
        u2 = User.get_by_name("Alfredo")
        assert alfredo == u2
        
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
        
        naly = User(name="Naly", is_bot=True)
        
        g = Game(uuid.uuid4(), phase_list, deck, discard_list, alfredo.id, naly.id, True, GameType.LEGACY, alfredo.id)
        h = Game.fromJSON(g.toJSON())
        assert g == h
        
        alfredo_p = Player(
            id=uuid.uuid4(),
            game_id=g.id,
            user_id=alfredo.id,
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
        
        naly_p = Player(
            id=uuid.uuid4(),
            game_id=g.id,
            user_id=naly.id,
            hand=CardCollection([
                Card.from_string("B7"),
                Card.from_string("Y8"),
                Card.from_string("G12"),
                Card.from_string("B2"),
            ]),
            turn_index=2,
            phase_index=7,
            drew_card=False,
            completed_phase=False,
            skip_cards=CardCollection([])
        )
        
        assert alfredo_p == Player.fromJSON(alfredo_p.toJSON())
        assert naly_p == Player.fromJSON(naly_p.toJSON())
        
        gpd = GamePhaseDeck(phase="S", game_id=g.id,
                            deck=CardCollection([Card.from_string("R3"), Card.from_string("B7")]))
        assert gpd == GamePhaseDeck.fromJSON(gpd.toJSON())
        
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
                    is_bot boolean DEFAULT false NOT NULL,
                    created_at timestamp NOT NULL,
                    updated_at timestamp NOT NULL,
                    CONSTRAINT users_pk PRIMARY KEY (id)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS users_name_isbot_idx ON public.users ("name",is_bot);
                CREATE INDEX IF NOT EXISTS users_name_idx ON public.users ("name");
                """
            )
            cur.execute("""
            do $$ BEGIN
                create type game_type as enum ('NORMAL', 'LEGACY');
            exception
                when duplicate_object then null;
            end $$;
            """)
            cur.execute("""
            CREATE TEMP TABLE games (
                id uuid NOT NULL,
                phase_list json NOT NULL,
                deck json NOT NULL,
                "discard" json NOT NULL,
                current_player uuid NOT NULL,
                host uuid NOT NULL,
                in_progress boolean DEFAULT false NOT NULL,
                type game_type DEFAULT 'NORMAL',
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
            
            alfredo.save()
            naly.save()
            g.save()
            alfredo_p.save()
            naly_p.save()
            gpd.save()
            
            assert alfredo == User.get_by_id(alfredo.id)
            assert alfredo == User.get_by_name(alfredo.name)
            assert naly == User.get_by_id(naly.id)
            assert naly == User.get_by_name(naly.name)
            
            assert Game.get_by_id(g.id) == g
            
            alfredo_p.turn_index = Player.get_by_id(alfredo_p.id).turn_index
            assert alfredo_p == Player.get_by_id(alfredo_p.id)
            assert alfredo_p == Player.get_by_game_id_user_id(g.id, alfredo.id)
            
            assert gpd == GamePhaseDeck.get_by_id(gpd.id)


if __name__ == "__main__":
    unittest.main()
