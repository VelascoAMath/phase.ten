import dataclasses

from Player import Player


@dataclasses.dataclass
class Game:
	id: int = 0
	players: list = dataclasses.field(default_factory=list)
	deck: list = dataclasses.field(default_factory=list)
	discard: list = dataclasses.field(default_factory=list)
	current_player: Player = None




def main():
	g = Game()
	
	print(g)

if __name__ == '__main__':
    main()