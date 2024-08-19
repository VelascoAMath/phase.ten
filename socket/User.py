import dataclasses
import json
import secrets
import uuid
from configparser import ConfigParser

import psycopg2

from add_db_functions import add_db_functions


@dataclasses.dataclass(order=True)
@add_db_functions(db_name='users', unique_indices=[['name']])
class User:
    id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
    name: str = ""
    token: str = dataclasses.field(default_factory=lambda: secrets.token_hex(16))
    
    # @staticmethod
    def toJSON(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "token": self.token,
        }
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return User.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return User(
            uuid.UUID(data["id"]),
            data["name"],
            data["token"],
        )


def main():
    u = User(
        uuid.uuid4(),
        "Alfredo",
        "secret token",
    )
    
    print(u)
    print(u.toJSON())
    print(User.fromJSON(u.toJSON()))
    print(u == User.fromJSON(u.toJSON()))
    
    parser = ConfigParser()
    config = {}
    
    parser.read('database.ini')
    if parser.has_section('postgresql'):
        for param in parser.items('postgresql'):
            config[param[0]] = param[1]
    else:
        raise Exception(f"No postgresql section in database.ini!")
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TEMP TABLE users (
                id uuid NOT NULL,
                name text NOT NULL,
                "token" text NOT NULL,
                CONSTRAINT users_pk PRIMARY KEY (id)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS users_name_idx ON users (name);
            """
        )
        
        User.set_cursor(cur)
        
        u = User(name="Alfredo")
        print(u)
        u.save()
        
        u2 = User.get_by_id(u.id)
        print(u2)
        print(u == u2)
        u2 = User.get_by_name("Alfredo")
        print(u2)
        print(u == u2)
        print(dir(u))


if __name__ == "__main__":
    main()
