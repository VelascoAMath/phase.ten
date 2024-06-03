import random

from Card import *
from Player import Player


@dataclasses.dataclass
class Game:
	id: int = 0
	phase_list: list = dataclasses.field(default_factory=list)
	players: list = dataclasses.field(default_factory=list)
	deck: list = dataclasses.field(default_factory=list)
	discard: list = dataclasses.field(default_factory=list)
	current_player: int = 0

	def toJSON(self):
		return json.dumps(
			{
				"id": self.id,
				"phase_list": self.phase_list,
				"players": [x.toJSONDict() for x in self.players],
				"deck": [x.toJSONDict() for x in self.deck],
				"discard": [x.toJSONDict() for x in self.discard],
				"current_player": self.current_player,
			}
		)

	@staticmethod
	def fromJSON(data):
		data = json.loads(data)
		player_list = []
		for p in data["players"]:
			player_list.append(Player.fromJSONDict(p))
		deck = []
		for c in data["deck"]:
			deck.append(Card.fromJSONDict(c))
		discard = []
		for c in data["discard"]:
			discard.append(Card.fromJSONDict(c))
		return Game(data["id"], data["phase_list"], player_list, deck, discard, data["current_player"])


def main():
	deck = []
	for color in Color:
		if color is Color.WILD or color is Color.SKIP:
			continue
		for rank in Rank:
			if rank is Rank.WILD or rank is Rank.SKIP:
				continue
			deck.append(Card(color, rank))
			deck.append(Card(color, rank))

		for _ in range(4):
			deck.append(Card(Color.SKIP, Rank.SKIP))

		for _ in range(8):
			deck.append(Card(Color.WILD, Rank.WILD))

	random.seed(0)
	random.shuffle(deck)

	alice = Player(
		30,
		"Alice",
		"secret token",
		[
			Card.from_string("R10"),
			Card.from_string("W"),
			Card.from_string("S"),
			Card.from_string("B4"),
		],
		4,
		8,
	)
	bob = Player(
		87,
		"Bob",
		"shush",
		[
			Card.from_string("W"),
			Card.from_string("W"),
			Card.from_string("B12"),
			Card.from_string("S"),
		],
		2,
		3,
	)
	charlie = Player(
		98,
		"Charlie",
		"no one knows",
		[
			Card.from_string("G11"),
			Card.from_string("G3"),
		],
		0,
		2,
	)
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
	player_list = [alice, bob, charlie]
	discard_list = [deck.pop() for _ in range(5)]
	g = Game(2884, phase_list, player_list, deck, discard_list, 87)
	print(g)
	h = Game.fromJSON(g.toJSON())
	print(h)
	print(g == h)


if __name__ == "__main__":
	main()
