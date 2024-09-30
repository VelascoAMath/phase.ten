import dataclasses
import datetime
import json
import secrets
import sqlite3
import uuid
from typing import Self

import psycopg2

from add_db_functions import add_db_functions


@dataclasses.dataclass(order=True)
@add_db_functions(db_name='users', unique_indices=[['name']])
class User:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    name: str = ""
    token: str = dataclasses.field(default_factory=lambda: secrets.token_hex(16))
    is_bot: bool = False
    created_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    updated_at: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now())
    
    def __post_init__(self):
        self.updated_at = self.created_at
    
    # @staticmethod
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "token": self.token,
            "is_bot": self.is_bot,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return User.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        created_at = data["created_at"]
        updated_at = data["updated_at"]
        
        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)
        
        if isinstance(updated_at, str):
            updated_at = datetime.datetime.fromisoformat(updated_at)
        
        return User(
            uuid.UUID(data["id"]),
            data["name"],
            data["token"],
            data["is_bot"],
            created_at=created_at,
            updated_at=updated_at,
        )
    
    @classmethod
    def set_cursor(cls, cur: sqlite3.Cursor | psycopg2.extensions.cursor):
        pass
    
    def save(self):
        pass
    
    @classmethod
    def all(cls) -> list[Self]:
        pass
    
    @classmethod
    def get_by_id(cls, id: str | uuid.UUID) -> Self:
        pass
    
    @classmethod
    def get_by_name(cls, name: str) -> Self:
        pass
    
    @classmethod
    def exists(cls, user_id: str | uuid.UUID) -> bool:
        pass
    
    @classmethod
    def exists_by_name(cls, name: str) -> bool:
        pass


def main():
    u = User(
        uuid.uuid4(),
        "Alfredo",
        "secret token",
    )
    
    print(u)
    print(u.toJSON())
    print(User.fromJSON(u.toJSON()))
    assert u == User.fromJSON(u.toJSON())


if __name__ == "__main__":
    main()
