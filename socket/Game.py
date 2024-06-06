import random

from Card import *


@dataclasses.dataclass(order=True)
class Game:
	id: str = ""
	phase_list: list = dataclasses.field(default_factory=list)
	deck: list = dataclasses.field(default_factory=list)
	discard: list = dataclasses.field(default_factory=list)
	current_player: str = ""
	# The player who originally created the game
	owner: str = ""
	# If the game has started
	in_progress: bool = False

	def toJSONDict(self):
		return {
			"id": self.id,
			"phase_list": self.phase_list,
			"deck": [x.toJSONDict() for x in self.deck],
			"discard": [x.toJSONDict() for x in self.discard],
			"current_player": self.current_player,
			"owner": self.owner,
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
		return Game(data["id"], data["phase_list"], deck, discard, data["current_player"], data["owner"], data["in_progress"])
	


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
	g = Game("2884", phase_list, deck, discard_list, "87", "87", True)
	print(g)
	h = Game.fromJSON(g.toJSON())
	print(h)
	print(g == h)


if __name__ == "__main__":
	main()
