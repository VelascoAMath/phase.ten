import datetime
import json
import uuid
from configparser import ConfigParser

import peewee

from CardCollection import CardCollection

parser = ConfigParser()
# Use this one when testing
# parser.read('database_test.ini')
parser.read("database.ini")
postgres_args = dict(parser.items("postgresql"))
db = peewee.PostgresqlDatabase(**postgres_args)

# Create game types
db.execute_sql(
    """
do $$ BEGIN
    create type game_type as enum ('NORMAL', 'LEGACY', 'ADVANCEMENT');
exception
    when duplicate_object then null;
end $$;
"""
)

# Create sequence for player turns
db.execute_sql(
    """
create sequence if not exists players_turn_index_seq AS integer;
"""
)


class StringListField(peewee.Field):
    field_type = "json"

    def db_value(self, value: list[str]) -> str:
        return json.dumps(value)


class CardListField(peewee.Field):
    field_type = "json"

    def db_value(self, value: CardCollection) -> str:
        return value.to_json()

    def python_value(self, value: list[dict[str:str]]) -> CardCollection:
        return CardCollection.from_json_dict(value)


class BaseModel(peewee.Model):
    id: uuid.UUID | peewee.UUIDField = peewee.UUIDField(primary_key=True, default=lambda: uuid.uuid4())
    created_at: datetime.datetime | peewee.DateTimeField = peewee.DateTimeField(
        null=False, default=lambda: datetime.datetime.now()
    )
    updated_at: datetime.datetime | peewee.DateTimeField = peewee.DateTimeField(
        null=False, default=lambda: datetime.datetime.now()
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.updated_at = self.created_at

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super().save(*args, **kwargs)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, BaseModel):
            return (
                self.id == other.id
                and self.created_at == other.created_at
                and self.updated_at == other.created_at
            )
        else:
            return False

    class Meta:
        database = db
