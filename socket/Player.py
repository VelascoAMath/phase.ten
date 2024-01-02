import dataclasses


@dataclasses.dataclass
class Player:
	id: int = 0
	hand: list = dataclasses.field(default_factory=list)
	skip_cards: int = 0
	
	
	