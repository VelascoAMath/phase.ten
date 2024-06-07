import dataclasses
import json

from Card import Card


@dataclasses.dataclass(order=True)
class Player:
    id: str = ""
    game_id: str = ""
    user_id: str = ""
    hand: list = dataclasses.field(default_factory=list)
    # Does this player go first, second, etc
    turn_index: int = -1
    phase_index: int = 0
    completed_phase: bool = False
    skip_cards: int = 0
    
    def toJSON(self):
        return json.dumps(self.toJSONDict())
    
    def toJSONDict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "hand": [x.toJSONDict() for x in self.hand],
            "turn_index": self.turn_index,
            "phase_index": self.phase_index,
            "completed_phase": (1 if self.completed_phase else 0),
            "skip_cards": self.skip_cards,
        }
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Player.fromJSONDict(data)
    
    @staticmethod
    def fromJSONDict(data):
        return Player(
            data["id"],
            data["game_id"],
            data["user_id"],
            [Card.fromJSONDict(x) for x in data["hand"]],
            data["turn_index"],
            data["phase_index"],
            (True if (data["completed_phase"] == 1) else False),
            data["skip_cards"],
        )


def main():
    p = Player(
        "30",
        "20",
        "50",
        [
            Card.from_string("R10"),
            Card.from_string("W"),
            Card.from_string("S"),
            Card.from_string("B4"),
        ],
        4,
        8,
        True,
        3
    )
    
    print(p)
    print(p.toJSON())
    print(Player.fromJSON(p.toJSON()))
    print(p == Player.fromJSON(p.toJSON()))


if __name__ == "__main__":
    main()
