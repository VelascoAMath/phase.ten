import dataclasses
import json

from Card import Card


@dataclasses.dataclass
class GamePhaseDeck:
    id: str = ""
    game_id: str = ""
    phase: str = ""
    deck: list = dataclasses.field(default=list)

    def toJSON(self):
        return json.dumps(self.toJSONDict())

    def toJSONDict(self):
        return {
            "id": self.id,
            "game_id": self.game_id,
            "phase": self.phase,
            "deck": [x.toJSONDict() for x in self.deck],
        }

    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        return GamePhaseDeck.fromJSONDict(data)

    @staticmethod
    def fromJSONDict(data):
        return GamePhaseDeck(
            data["id"],
            data["game_id"],
            data["phase"],
            [Card.fromJSONDict(x) for x in data["deck"]],
        )

