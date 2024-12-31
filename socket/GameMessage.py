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
    
    def to_json_dict(self) -> dict:
        return {
            "id": str(self.id),
            "game": str(self.game.id),
            "message": self.message,
            "index": self.index,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
    
    class Meta:
        table_name = "gamemessage"
        indexes = (
            (("game_id", "index"), True),
        )
