import dataclasses
import datetime
import json
import secrets
import uuid

import peewee

from BaseModel import BaseModel


@dataclasses.dataclass(init=False)
class Users(BaseModel):
    name: str = peewee.TextField(null=False, unique=True)
    display: str = peewee.TextField(null=False)
    token: str = peewee.TextField(null=False, default=lambda: secrets.token_hex(16))
    is_bot: peewee.BooleanField = peewee.BooleanField(null=False, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.display = self.name

    def toJSON(self):
        return json.dumps(self.to_json_dict())

    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display": self.display,
            "token": self.token,
            "is_bot": self.is_bot,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return Users.from_json_dict(data)

    @staticmethod
    def from_json_dict(data):
        created_at = data["created_at"]
        updated_at = data["updated_at"]

        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)

        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)

        return Users(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            display=data["display"],
            token=data["token"],
            is_bot=data["is_bot"],
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, display={self.display}, token={self.token}, is_bot={self.is_bot}, created_at={self.created_at}, updated_at={self.updated_at})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Users):
            return (
                super().__eq__(other)
                and self.name == other.name
                and self.display == other.display
                and self.token == other.token
                and self.is_bot == other.is_bot
            )
        else:
            return False

    class Meta:
        table_name = "users"
        indexes = ((("name", "is_bot"), True),)

    @classmethod
    def exists(cls, user_id: str | uuid.UUID):
        return Users.get_or_none(id=user_id) is not None
