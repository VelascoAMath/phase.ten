import dataclasses
import json

import vel_data_structures
from vel_data_structures import AVL_Set

from Card import Card
from Player import Player


@dataclasses.dataclass(order=True)
class User:
    id: int = 0
    name: str = ""
    token: str = ""
    player_set: set = dataclasses.field(default_factory=AVL_Set)
    

    def toJSON(self):
        return json.dumps(
            {
                "id": self.id,
                "name": self.name,
                "token": self.token,
                "player_set": [x.toJSONDict() for x in self.player_set],
            }
        )

    def toJSONDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "token": self.token,
            "player_set": [x.toJSONDict() for x in self.player_set],
        }

    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return User(
            data["id"],
            data["name"],
            data["token"],
            AVL_Set(Player.fromJSONDict(x) for x in data["player_set"]),
        )

    @staticmethod
    def fromJSONDict(data):
        return User(
            data["id"],
            data["name"],
            data["token"],
            AVL_Set(Player.fromJSONDict(x) for x in data["player_set"])
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
    u = User(
        30,
        "Alfredo",
        "secret token",
        AVL_Set([p])
    )

    print(u)
    print(u.toJSON())
    print(User.fromJSON(u.toJSON()))


if __name__ == "__main__":
    main()
