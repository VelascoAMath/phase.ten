import dataclasses
import json

from Card import Card


@dataclasses.dataclass
class Player:
    id: int = 0
    name: str = ""
    token: str = ""
    hand: list = dataclasses.field(default_factory=list)
    skip_cards: int = 0
    phase: int = 1

    def toJSON(self):
        return json.dumps(
            {
                "id": self.id,
                "name": self.name,
                "token": self.token,
                "hand": [x.toJSON() for x in self.hand],
                "skip_cards": self.skip_cards,
                "phase": self.phase,
            }
        )

    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Player(
            data["id"],
            data["name"],
            data["token"],
            [Card.fromJSON(x) for x in data["hand"]],
            data["skip_cards"],
            data["phase"],
        )


def main():
    p = Player(
        30,
        "Alfredo",
        "secret token",
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
