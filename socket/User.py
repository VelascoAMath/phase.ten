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
    

    def toJSON(self):
        return json.dumps(self.toJSONDict())

    def toJSONDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "token": self.token,
        }

    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return User.fromJSONDict(data)

    @staticmethod
    def fromJSONDict(data):
        return User(
            data["id"],
            data["name"],
            data["token"],
        )


def main():
    u = User(
        30,
        "Alfredo",
        "secret token",
    )

    print(u)
    print(u.toJSON())
    print(User.fromJSON(u.toJSON()))


if __name__ == "__main__":
    main()
