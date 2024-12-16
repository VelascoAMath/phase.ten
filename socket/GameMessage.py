import peewee

from BaseModel import BaseModel
from Games import Games


class GameMessage(BaseModel):
    game: Games = peewee.ForeignKeyField(
        column_name="game_id", field="id", model=Games, null=False, on_delete="CASCADE", on_update="CASCADE"
    )
    message: str = peewee.TextField(null=False)
    index: int = peewee.IntegerField(
        constraints=[peewee.SQL("DEFAULT nextval('game_message_index_seq'::regclass)")]
    )
    
    class Meta:
        table_name = "gamemessage"
        indexes = (
            (("game_id", "index"), True),
        )
