import sqlite3
from pprint import pprint
from typing import ClassVar, Self

from Card import *
from Player import Player


@dataclasses.dataclass(order=True)
class Game:
	id: uuid.UUID = dataclasses.field(default_factory=lambda: uuid.uuid4())
	phase_list: list[str] = dataclasses.field(default_factory=list)
	deck: list[Card] = dataclasses.field(default_factory=list)
	discard: list[Card] = dataclasses.field(default_factory=list)
	current_player: uuid.UUID = None
	# The player who originally created the game
	owner: uuid.UUID = None
	# If the game has started
	in_progress: bool = False
	cur: ClassVar[sqlite3.Cursor] = None

	def save(self):
		
		json_deck = [x.toJSONDict() for x in self.deck]
		json_discard = [x.toJSONDict() for x in self.discard]
		if Game.exists(self.id):
			Game.cur.execute(
				"UPDATE games SET phase_list=?, deck=?, discard=?, current_player=?, owner=?, in_progress=? WHERE id=?",
				(json.dumps(self.phase_list), json.dumps(json_deck), json.dumps(json_discard), str(self.current_player), str(self.owner), self.in_progress, str(self.id)))
		else:
			Game.cur.execute(
				"INSERT INTO games (id, phase_list, deck, discard, current_player, owner, in_progress) VALUES (?, ?, ?, ?, ?, ?, ?)",
				(str(self.id), json.dumps(self.phase_list), json.dumps(json_deck), json.dumps(json_discard),
				 str(self.current_player), str(self.owner), self.in_progress))

	def delete(self):
		Game.cur.execute("DELETE FROM games WHERE id = ?", (str(self.id),))
		# Need to delete all players associated with this game
		Game.cur.execute("DELETE FROM players WHERE game_id = ?", (str(self.id),))
	
	def get_players(self):
		player_list = []
		for (id,) in list(Game.cur.execute("SELECT id FROM players WHERE game_id=? ORDER BY turn_index", (str(self.id),))):
			player_list.append(Player.get_by_id(id))
		return player_list
		
	@staticmethod
	def exists(id: str | uuid.UUID):
		if isinstance(id, uuid.UUID):
			id = str(id)
		return Game.cur.execute("SELECT * FROM games WHERE id = ?", (id,)).fetchone() is not None
	
	@staticmethod
	def setCursor(cur):
		Game.cur = cur
	
	@staticmethod
	def get_by_id(id):
		if isinstance(id, uuid.UUID):
			id = str(id)
		for (id, phase_list, deck_json, discard_json, current_player, owner, in_progress) in list(Game.cur.execute(
			"SELECT * FROM games WHERE id = ?", (id,))):
			deck = [Card.fromJSONDict(x) for x in json.loads(deck_json)]
			discard = [Card.fromJSONDict(x) for x in json.loads(discard_json)]
			game = Game()
			game.id = id
			game.phase_list = json.loads(phase_list)
			game.deck = deck
			game.discard = discard
			game.current_player = uuid.UUID(current_player)
			game.owner = uuid.UUID(owner)
			if isinstance(in_progress, int):
				game.in_progress = in_progress == 1
			else:
				game.in_progress = in_progress
			return game
		
		raise Exception(f"{id} is not a valid game id!")
	
	@staticmethod
	def all() -> list:
		game_list = []
		for (id, phase_list, deck_json, discard_json, current_player, owner, in_progress) in Game.cur.execute(
			"SELECT * FROM games"):
			deck = [Card.fromJSONDict(x) for x in json.loads(deck_json)]
			discard = [Card.fromJSONDict(x) for x in json.loads(discard_json)]
			game = Game()
			game.id = id
			game.phase_list = json.loads(phase_list)
			game.deck = deck
			game.discard = discard
			game.current_player = uuid.UUID(current_player)
			game.owner = uuid.UUID(owner)
			if isinstance(in_progress, int):
				game.in_progress = in_progress == 1
			else:
				game.in_progress = in_progress
			game_list.append(game)
		return game_list
	
	
	def toJSONDict(self):
		return {
			"id": str(self.id),
			"phase_list": self.phase_list,
			"deck": [x.toJSONDict() for x in self.deck],
			"discard": [x.toJSONDict() for x in self.discard],
			"current_player": str(self.current_player),
			"owner": str(self.owner),
			"in_progress": self.in_progress,
		}
	
	def toJSON(self):
		return json.dumps(self.toJSONDict())

	@staticmethod
	def fromJSON(data):
		data = json.loads(data)
		deck = []
		for c in data["deck"]:
			deck.append(Card.fromJSONDict(c))
		discard = []
		for c in data["discard"]:
			discard.append(Card.fromJSONDict(c))
		return Game(uuid.UUID(data["id"]), data["phase_list"], deck, discard, uuid.UUID(data["current_player"]), uuid.UUID(data["owner"]), data["in_progress"])
	


def main():
	deck = Card.getNewDeck()

	random.seed(0)
	random.shuffle(deck)

	phase_list = [
		"S3+S3",
		"S3+R4",
		"S4+R4",
		"R7",
		"R8",
		"R9",
		"S4+S4",
		"C7",
		"S5+S2",
		"S5+S3",
	]
	discard_list = [deck.pop() for _ in range(5)]
	g = Game(uuid.uuid4(), phase_list, deck, discard_list, uuid.uuid4(), uuid.uuid4(), True)
	print(g)
	h = Game.fromJSON(g.toJSON())
	print(h)
	print(g == h)


if __name__ == "__main__":
	main()
