import dataclasses
import json
import sqlite3
import uuid
from typing import ClassVar, Self

from Card import Card


@dataclasses.dataclass(order=True)
class Player:
	id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
	game_id: uuid.UUID = None
	user_id: uuid.UUID = None
	hand: list[Card] = dataclasses.field(default_factory=list)
	# Does this player go first, second, etc
	turn_index: int = -1
	phase_index: int = 0
	drew_card: bool = False
	completed_phase: bool = False
	skip_cards: int = 0
	cur: ClassVar[sqlite3.Cursor] = None
	
	def save(self):
		json_hand = [x.toJSONDict() for x in self.hand]
		
		if Player.exists(self.id):
			Player.cur.execute("UPDATE players SET game_id=?,user_id=?,hand=?,turn_index=?,phase_index=?,drew_card=?,"
			                   "completed_phase=?, skip_cards=? WHERE id=?", (str(self.game_id), str(self.user_id), json.dumps(json_hand), self.turn_index, self.phase_index, self.drew_card, self.completed_phase, self.skip_cards, str(self.id)))
		else:
			Player.cur.execute("INSERT INTO players (id, game_id, user_id, hand, turn_index, phase_index, drew_card, "
			                   "completed_phase, skip_cards) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
			                   (str(self.id), str(self.game_id), str(self.user_id), json.dumps(json_hand), self.turn_index, self.phase_index, self.drew_card, self.completed_phase, self.skip_cards))

	def delete(self):
		Player.cur.execute("DELETE FROM players WHERE id=?", (str(self.id),))

	@staticmethod
	def exists(id: str | uuid.UUID):
		if isinstance(id, uuid.UUID):
			id = str(id)
		return Player.cur.execute("SELECT * FROM players WHERE id = ?", (id,)).fetchone() is not None
	
	@staticmethod
	def get_by_id(id: str | uuid.UUID):
		if isinstance(id, uuid.UUID):
			id = str(id)
		for (id, game_id, user_id, hand_json, turn_index, phase_index, drew_deck, completed_phase, skip_cards) in list(
			Player.cur.execute(
				"SELECT * FROM players WHERE id = ?", (id,))):
			hand = [Card.fromJSONDict(x) for x in json.loads(hand_json)]
			
			p = Player(uuid.UUID(id), uuid.UUID(game_id), uuid.UUID(user_id), hand, turn_index, phase_index, drew_deck == 1,
			           completed_phase == 1, skip_cards)
			return p
	
	@staticmethod
	def get_by_game_user_id(game_id: str | uuid.UUID, user_id: str | uuid.UUID) -> Self:
		if isinstance(game_id, uuid.UUID):
			game_id = str(game_id)
		if isinstance(user_id, uuid.UUID):
			user_id = str(user_id)
		
		for (id, game_id, user_id, hand_json, turn_index, phase_index, drew_deck, completed_phase, skip_cards) in list(
			Player.cur.execute(
				"SELECT * FROM players WHERE game_id = ? AND user_id = ?", (game_id, user_id))):
			hand = [Card.fromJSONDict(x) for x in json.loads(hand_json)]
			p = Player(uuid.UUID(id), uuid.UUID(game_id), uuid.UUID(user_id), hand, turn_index, phase_index,
			           drew_deck == 1, completed_phase == 1, skip_cards)
			return p
	
	@staticmethod
	def exists_game_user(game_id: str | uuid.UUID, user_id: str | uuid.UUID) -> bool:
		if isinstance(game_id, uuid.UUID):
			game_id = str(game_id)
		if isinstance(user_id, uuid.UUID):
			user_id = str(user_id)
		
		return not (Player.cur.execute("SELECT * FROM players WHERE game_id = ? AND user_id = ?",
		                               (game_id, user_id)).fetchone() is None)
	
	@staticmethod
	def setCursor(cur):
		Player.cur = cur
	
	def toJSON(self):
		return json.dumps(self.toJSONDict())
	
	def toJSONDict(self):
		return {
			"id": str(self.id),
			"game_id": str(self.game_id),
			"user_id": str(self.user_id),
			"hand": [x.toJSONDict() for x in self.hand],
			"turn_index": self.turn_index,
			"phase_index": self.phase_index,
			"drew_card": self.drew_card,
			"completed_phase": self.completed_phase,
			"skip_cards": self.skip_cards,
		}
	
	@staticmethod
	def fromJSON(data):
		data = json.loads(data)
		return Player.fromJSONDict(data)
	
	@staticmethod
	def fromJSONDict(data):
		return Player(
			uuid.UUID(data["id"]),
			uuid.UUID(data["game_id"]),
			uuid.UUID(data["user_id"]),
			[Card.fromJSONDict(x) for x in data["hand"]],
			data["turn_index"],
			data["phase_index"],
			data["drew_card"],
			data["completed_phase"],
			data["skip_cards"],
		)


def main():
	p = Player(
		uuid.uuid4(),
		uuid.uuid4(),
		uuid.uuid4(),
		[
			Card.from_string("R10"),
			Card.from_string("W"),
			Card.from_string("S"),
			Card.from_string("B4"),
		],
		4,
		8,
		True,
		True,
		3
	)
	
	print(p)
	print(p.toJSON())
	print(Player.fromJSON(p.toJSON()))
	print(p == Player.fromJSON(p.toJSON()))


if __name__ == "__main__":
	main()
