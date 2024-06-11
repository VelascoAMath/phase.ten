import dataclasses
import json
import secrets
import uuid
from uuid import UUID


@dataclasses.dataclass(order=True)
class User:
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    token: str = dataclasses.field(default_factory=lambda:secrets.token_hex(16))
    

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
        "30",
        "Alfredo",
        "secret token",
    )

    print(u)
    print(u.toJSON())
    print(User.fromJSON(u.toJSON()))
    print(u == User.fromJSON(u.toJSON()))
    u = User()
    print(u)


if __name__ == "__main__":
    main()
