import dataclasses
import json

from Card import Card


@dataclasses.dataclass
class Player:
    id: int = 0
    user_id: int = 0
    game_id: int = 0
    hand: list = dataclasses.field(default_factory=list)
    skip_cards: int = 0
    phase: int = 1
    
    def toJSON(self):
        return json.dumps(self.toJSONDict())
    
    def toJSONDict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "hand": [x.toJSONDict() for x in self.hand],
            "skip_cards": self.skip_cards,
            "phase": self.phase,
        }
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Player.fromJSONDict(data)
    
    @staticmethod
    def fromJSONDict(data):
        return Player(
            data["id"],

            data["user_id"],
            data["game_id"],
            [Card.fromJSONDict(x) for x in data["hand"]],
            data["skip_cards"],
            data["phase"],
        )


def main():
    p = Player(
        30,
        20,
        50,
        [
            Card.from_string("R10"),
            Card.from_string("W"),
            Card.from_string("S"),
            Card.from_string("B4"),
        ],
        4,
        8,
    )
    
    print(p)
    print(p.toJSON())
    print(Player.fromJSON(p.toJSON()))


if __name__ == "__main__":
    main()
