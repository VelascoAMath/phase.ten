import dataclasses
import datetime
import json
import random
import uuid

import peewee

from BaseModel import BaseModel, CardListField
from Card import Rank, Card
from CardCollection import CardCollection
from Gamephasedecks import Gamephasedecks
from Games import Games
from RE import RE
from Users import Users


@dataclasses.dataclass(init=False)
class Players(BaseModel):
    game: Games = peewee.ForeignKeyField(
        column_name="game_id", field="id", model=Games, null=False, on_delete='CASCADE'
    )
    user: Users = peewee.ForeignKeyField(
        column_name="user_id", field="id", model=Users, null=False, on_delete='CASCADE'
    )
    hand: CardCollection = CardListField(null=False, default=CardCollection())
    # Does this player go first, second, etc
    turn_index: int = peewee.IntegerField(
        constraints=[peewee.SQL("DEFAULT nextval('players_turn_index_seq'::regclass)")])
    phase_index: int = peewee.IntegerField(null=False, default=0)
    drew_card: bool = peewee.BooleanField(default=False, null=False)
    completed_phase: bool = peewee.BooleanField(default=False, null=False)
    skip_cards: CardCollection = CardListField(null=False, default=CardCollection())
    
    def make_next_move(self):
        """
        Calculates what the next move should be for a bot player

        :return: a dictionary which can be converted into JSON. The format is meant to be passed into the handle_data method in app.py
        :rtype: dict
        """
        game = Games.get_by_id(self.game_id)
        user = Users.get_by_id(self.user_id)
        
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
                                for player in Players.all()
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
                            self.hand[:i] + self.hand[i + 1:] + [game.discard[-1]]
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
                gpd_list = Gamephasedecks.all_where_game_id(game.id)
                
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
        return Players.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        
        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)
        
        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)
        
        return Players(
            id=uuid.UUID(data["id"]),
            game=Games.get_by_id(data["game_id"]),
            user=Users.get_by_id(data["user_id"]),
            hand=CardCollection(Card.fromJSONDict(card) for card in data["hand"]),
            turn_index=data["turn_index"],
            phase_index=data["phase_index"],
            drew_card=data["drew_card"],
            completed_phase=data["completed_phase"],
            skip_cards=CardCollection(
                Card.fromJSONDict(card) for card in data["skip_cards"]
            ),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def __str__(self):
        return f'Players(id={self.id}, game_id={self.game.id} user_id={self.user.id} hand={self.hand}, turn_index={self.turn_index}, phase_index={self.phase_index}, drew_card={self.drew_card}, completed_phase={self.completed_phase}, skip_cards={self.skip_cards}, created_at={self.created_at}, updated_at={self.updated_at})'
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Players):
            return super().__eq__(
                other) and self.game == other.game and self.user == other.user and self.hand == other.hand and self.turn_index == other.turn_index and self.phase_index == other.phase_index and self.drew_card == other.drew_card and self.completed_phase == other.completed_phase and self.skip_cards == other.skip_cards
        else:
            return False
    
    class Meta:
        table_name = "players"
        indexes = (
            (("game", "turn_index"), True),
            (("game", "user"), True),
        )
