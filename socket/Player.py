import dataclasses
import datetime
import json
import random
import sqlite3
import uuid
from typing import Self

import psycopg2

from Card import Card, Rank
from CardCollection import CardCollection
from Game import Game
from GamePhaseDeck import GamePhaseDeck
from RE import RE
from User import User
from add_db_functions import add_db_functions


@dataclasses.dataclass(order=True)
@add_db_functions(
    db_name="players",
    single_foreign=[("game_id", Game), ("user_id", User)],
    unique_indices=[["game_id", "turn_index"], ["game_id", "user_id"]],
    serial_set={"turn_index"},
)
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
    created_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now()
    )
    updated_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now()
    )

    def __post_init__(self):
        self.updated_at = self.created_at

    def make_next_move(self):
        """
        Calculates what the next move should be for a bot player

        :return: a dictionary which can be converted into JSON. The format is meant to be passed into the handle_data method in app.py
        :rtype: dict
        """
        game = Game.get_by_id(self.game_id)
        user = User.get_by_id(self.user_id)

        if game.current_player != self.user_id:
            raise Exception(f"Can't play! It's not my turn!")

        if self.skip_cards:
            return {"player_id": self.id, "type": "player_action", "action": "do_skip"}

        if not self.drew_card:
            if len(game.discard) == 0:
                return {
                    "player_id": self.id,
                    "type": "player_action",
                    "action": "draw_deck",
                }

            # A skip card can never be drawn from the discard pile
            if game.discard[-1].rank is Rank.SKIP:
                return {
                    "player_id": self.id,
                    "type": "player_action",
                    "action": "draw_deck",
                }

            if game.discard[-1].rank is Rank.WILD:
                return {
                    "player_id": self.id,
                    "type": "player_action",
                    "action": "draw_discard",
                }

            re = RE(game.phase_list[self.phase_index])

            score = re.score(self.hand)

            # Card in discard pile will get us closer to completing our phase
            if re.score(CardCollection(self.hand + [game.discard[-1]])) < score:
                return {
                    "player_id": self.id,
                    "type": "player_action",
                    "action": "draw_discard",
                }

            return {
                "player_id": self.id,
                "type": "player_action",
                "action": "draw_deck",
            }

        else:
            if not self.completed_phase:
                rr = RE(game.phase_list[self.phase_index])

                (result, hand_subset) = rr.isSubsetAccepted(self.hand)

                if result:
                    return {
                        "player_id": self.id,
                        "type": "player_action",
                        "action": "complete_phase",
                        "cards": hand_subset.to_json_dict(),
                    }
                else:
                    # If we have a skip, use it on the player with the highest phase index and if there's a tie,
                    # randomly choose one who has completed their phase
                    for card in self.hand:
                        if card.rank is Rank.SKIP:
                            other_players = [
                                player
                                for player in Player.all()
                                if player.game_id == game.id and player.id != self.id
                            ]
                            other_players.sort(
                                key=lambda x: (x.phase_index, x.completed_phase)
                            )

                            return {
                                "player_id": self.id,
                                "type": "player_action",
                                "action": "skip_player",
                                "to": other_players[-1].user_id,
                            }

                    score = rr.score(self.hand)
                    # Discard any card in our hand which isn't necessary to completing our phase
                    for i in range(len(self.hand)):
                        if self.hand[i].rank is Rank.WILD:
                            continue
                        if (
                            not self.drew_card
                            and rr.score(
                                self.hand[:i] + self.hand[i + 1 :] + [game.discard[-1]]
                            )
                            > score
                        ):
                            return {
                                "player_id": self.id,
                                "type": "player_action",
                                "action": "discard",
                                "card_id": self.hand[i].id,
                            }
            else:
                gpd_list = GamePhaseDeck.all_where_game_id(game.id)

                # if we can put down, do it
                for gpd in gpd_list:
                    re = RE(gpd.phase)
                    for card in self.hand:
                        if re.isFullyAccepted(
                            CardCollection(CardCollection([card]) + gpd.deck)
                        ):
                            return {
                                "player_id": self.id,
                                "type": "player_action",
                                "action": "put_down",
                                "phase_deck_id": gpd.id,
                                "cards": CardCollection([card]).to_json_dict(),
                                "direction": "start",
                            }
                        if re.isFullyAccepted(
                            CardCollection(gpd.deck + CardCollection([card]))
                        ):
                            return {
                                "player_id": self.id,
                                "type": "player_action",
                                "action": "put_down",
                                "phase_deck_id": gpd.id,
                                "cards": CardCollection([card]).to_json_dict(),
                                "direction": "end",
                            }

                for card in self.hand:
                    if card.rank is not Rank.WILD:
                        return {
                            "player_id": self.id,
                            "type": "player_action",
                            "action": "discard",
                            "card_id": card.id,
                        }

            # Otherwise, pick a random card to discard
            return {
                "player_id": self.id,
                "type": "player_action",
                "action": "discard",
                "card_id": random.choice(self.hand).id,
            }

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
    def get_by_game_id_user_id(
        cls, game_id: str | uuid.UUID, to_id: str | uuid.UUID
    ) -> Self:
        pass

    @classmethod
    def exists_by_game_id_user_id(
        cls, game_id: str | uuid.UUID, user_id: str | uuid.UUID
    ) -> bool:
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

    print(p)
    print(p.toJSON())
    print(Player.fromJSON(p.toJSON()))
    assert p == Player.fromJSON(p.toJSON())


if __name__ == "__main__":
    main()
