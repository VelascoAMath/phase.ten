import random
import unittest
from configparser import ConfigParser

import peewee

from Card import Card
from CardCollection import CardCollection
from Gamephasedecks import Gamephasedecks
from Games import Games, GameType
from Players import Players
from Users import Users


class TestRE(unittest.TestCase):
    def setUp(self):
        parser = ConfigParser()
        parser.read("database_test.ini")
        postgres_args = dict(parser.items("postgresql"))
        self.db = peewee.PostgresqlDatabase(**postgres_args)
        db = self.db

        """Main entry point of program"""
        db.execute_sql(
            """
        do $$ BEGIN
            create type game_type as enum ('NORMAL', 'LEGACY', 'ADVANCEMENT');
        exception
            when duplicate_object then null;
        end $$;
        """
        )
        db.execute_sql(
            """
        create sequence if not exists players_turn_index_seq AS integer;
        """
        )
        db.drop_tables([Users, Games, Players, Gamephasedecks])
        db.create_tables([Users, Games, Players, Gamephasedecks])

    def tearDown(self):
        self.db.close()

    def test_objects(self):
        alfredo = Users(
            name="Alfredo",
            display="Alfredo",
            token="secret token",
            is_bot=False,
        )

        assert alfredo == Users.fromJSON(alfredo.toJSON())

        alfredo.save(force_insert=True)

        u2 = Users.get_by_id(alfredo.id)
        assert alfredo == u2

        u2 = Users.get(name="Alfredo")
        assert alfredo == u2

        deck = CardCollection.getNewDeck()
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

        naly = Users(name="Naly", display="Lemonaly", is_bot=True)
        naly.save(force_insert=True)

        assert alfredo != naly
        assert alfredo == Users(
            id=alfredo.id,
            name="Alfredo",
            display="Alfredo",
            token="secret token",
            is_bot=False,
            created_at=alfredo.created_at,
            updated_at=alfredo.updated_at,
        )

        g = Games(
            phase_list=phase_list,
            deck=deck,
            discard=discard_list,
            host=Users.get_by_id(alfredo.id),
            current_player=Users.get_by_id(naly.id),
            in_progress=True,
            type=GameType.LEGACY,
            winner=Users.get_by_id(alfredo.id),
        )
        h = Games.fromJSON(g.toJSON())
        assert g == h
        assert g != Games(
            phase_list=phase_list,
            deck=deck,
            discard=discard_list,
            host=Users.get_by_id(naly.id),
            current_player=Users.get_by_id(alfredo.id),
            in_progress=False,
            type=GameType.NORMAL,
            winner=None,
        )

        g.save(force_insert=True)

        alfredo_p = Players(
            game=g,
            user=alfredo,
            hand=CardCollection(
                [
                    Card.from_string("R10"),
                    Card.from_string("W"),
                    Card.from_string("S"),
                    Card.from_string("B4"),
                ]
            ),
            turn_index=4,
            phase_index=8,
            drew_card=True,
            completed_phase=True,
            skip_cards=CardCollection(
                [Card.from_string("S"), Card.from_string("S"), Card.from_string("S")]
            ),
        )

        alfredo_p.save(force_insert=True)

        naly_p = Players(
            game=g,
            user=naly,
            hand=CardCollection(
                [
                    Card.from_string("B7"),
                    Card.from_string("Y8"),
                    Card.from_string("G12"),
                    Card.from_string("B2"),
                ]
            ),
            turn_index=2,
            phase_index=7,
            drew_card=False,
            completed_phase=False,
            skip_cards=CardCollection([]),
        )
        naly_p.save(force_insert=True)

        assert alfredo_p == Players.fromJSON(alfredo_p.toJSON())
        assert naly_p == Players.fromJSON(naly_p.toJSON())
        assert alfredo_p != naly_p

        gpd = Gamephasedecks(
            phase="S",
            game=g,
            deck=CardCollection([Card.from_string("R3"), Card.from_string("B7")]),
        )
        assert gpd == Gamephasedecks.fromJSON(gpd.toJSON())

        gpd.save(force_insert=True)

        assert alfredo == Users.get_by_id(alfredo.id)
        assert alfredo == Users.get(name=alfredo.name)
        assert naly == Users.get_by_id(naly.id)
        assert naly == Users.get(name=naly.name)

        assert Games.get_by_id(g.id) == g

        alfredo_p.turn_index = Players.get_by_id(alfredo_p.id).turn_index
        assert alfredo_p == Players.get_by_id(alfredo_p.id)
        assert alfredo_p == Players.get_or_none(game=g.id, user=alfredo)

        assert gpd == Gamephasedecks.get_by_id(gpd.id)


if __name__ == "__main__":
    unittest.main()
