import collections
import dataclasses
import re
import uuid
from typing import Self

import graphviz

from Card import Card, Color, Rank


@dataclasses.dataclass
class _State:
	is_final: bool = False
	
	_id: int = dataclasses.field(default_factory=lambda: uuid.uuid4().int)
	cardTransition: dict[Card, Self] = dataclasses.field(default_factory=dict)
	rankTransition: dict[Rank, Self] = dataclasses.field(default_factory=dict)
	colorTransition: dict[Color, Self] = dataclasses.field(default_factory=dict)
	
	emptyTransition: Self = None
	
	def put(self, item: Card | Rank | Color, next_state: Self):
		if isinstance(item, Card):
			self.cardTransition[item] = next_state
		elif isinstance(item, Rank):
			self.rankTransition[item] = next_state
		elif isinstance(item, Color):
			self.colorTransition[item] = next_state
		else:
			raise Exception(f"Cannot insert {item} because it's of type {type(item)}")
	
	def get(self, item: Card | Rank | Color) -> Self:
		if isinstance(item, Card):
			return self.cardTransition[item]
		elif isinstance(item, Rank):
			return self.rankTransition[item]
		elif isinstance(item, Color):
			return self.colorTransition[item]
		else:
			raise Exception(f"Cannot insert {item} because it's of type {type(item)}")
	
	def isAccepted(self, c: Card) -> bool:
		if self.emptyTransition is not None:
			return True
		return (
			(c in self.cardTransition)
			or (c.color in self.colorTransition)
			or (c.rank in self.rankTransition)
		)
	
	def getNext(self, item: Card) -> Self:
		if self.emptyTransition is not None:
			return self.emptyTransition
		
		if self.isAccepted(item):
			if item in self.cardTransition:
				return self.cardTransition[item]
			if item.color in self.colorTransition:
				return self.colorTransition[item.color]
			if item.rank in self.rankTransition:
				return self.rankTransition[item.rank]
		
		raise Exception(f"Cannot transition for {item}!")
	
	def __hash__(self):
		return self._id


def _run() -> _State:
	start_state = _State()
	rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
	
	state_grid = [
		[_State() for _ in range(len(rank_list) - i)] for i in range(len(rank_list))
	]
	
	for i in range(len(rank_list)):
		start_state.put(rank_list[i], state_grid[i][0])
		for j in range(len(state_grid[i]) - 1):
			state_grid[i][j].is_final = True
			# State to next card (e.g. R3 Y4)
			state_grid[i][j].put(rank_list[i + j + 1], state_grid[i][j + 1])
			# State to wild (e.g. R3 W)
			state_grid[i][j].put(Rank.WILD, state_grid[i][j + 1])
		state_grid[i][-1].is_final = True
	
	# Need a separate collection of wilds
	wild_state = [_State() for _ in rank_list]
	
	for j in range(len(wild_state) - 1):
		# Chain the wilds together since a collection of wilds is a run
		wild_state[j].put(Rank.WILD, wild_state[j + 1])
		wild_state[j].is_final = True
	wild_state[-1].is_final = True
	
	for i in range(len(state_grid)):
		for j in range(len(state_grid[i]) - 1):
			# Wild to next card (e.g. W R3)
			wild_state[j].put(rank_list[i + j + 1], state_grid[i][j + 1])
	
	start_state.put(Rank.WILD, wild_state[0])
	return start_state


def _strictRun(size: int) -> (_State, set[_State]):
	if size < 1 or size > 12:
		raise Exception(f"Invalid size {size}. Must be between 1 and 12 inclusive!")
	
	start_state = _State()
	rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
	state_grid = [
		[_State() for _ in range(size)] for _ in range(len(rank_list) - size + 1)
	]
	
	for i in range(len(state_grid)):
		# Start to the beginning of state grid
		start_state.put(rank_list[i], state_grid[i][0])
		for j in range(len(state_grid[0]) - 1):
			# State to next card (e.g. R2 G3)
			state_grid[i][j].put(rank_list[i + j + 1], state_grid[i][j + 1])
			# State to wild (e.g. R2 W)
			state_grid[i][j].put(Rank.WILD, state_grid[i][j + 1])
	# state_grid[i][-1].is_final = True
	
	# Need a separate collection of wilds
	wild_state = [_State() for _ in range(size)]
	start_state.put(Rank.WILD, wild_state[0])
	for j in range(size - 1):
		# Chain the wilds together since a collection of wilds is a run
		wild_state[j].put(Rank.WILD, wild_state[j + 1])
		for i in range(len(state_grid)):
			# Wild to next card (e.g. W R3)
			wild_state[j].put(rank_list[i + j + 1], state_grid[i][j + 1])
	# wild_state[-1].is_final = True
	
	final_state_set = set([state_grid[i][-1] for i in range(len(state_grid))])
	final_state_set.add(wild_state[-1])
	
	return start_state, final_state_set


def _strictColor(size: int) -> (_State, set[_State]):
	if size < 1 or size > 12:
		raise Exception(f"Invalid size {size}. Must be between 1 and 12 inclusive!")
	
	start_state = _State()
	color_list = [c for c in Color if (c is not Color.SKIP)]
	wild_index = -1
	for i, c in enumerate(color_list):
		if c is Color.WILD:
			wild_index = i
	
	# Each row represents a color
	# The number of columns is size
	state_grid = [[_State() for _ in range(size)] for _ in range(len(color_list))]
	
	for i in range(len(state_grid)):
		color = color_list[i]
		# Connect the start state to the beginning of the state grid
		start_state.put(color, state_grid[i][0])
		for j in range(len(state_grid[i]) - 1):
			color = color_list[i]
			# State to same color (e.g. R2 R7)
			state_grid[i][j].put(color, state_grid[i][j + 1])
			# State to wild (e.g. R2 W)
			state_grid[i][j].put(Color.WILD, state_grid[i][j + 1])
			# Wild to state (e.g. W R2)
			state_grid[wild_index][j].put(color, state_grid[i][j + 1])
	
	# Last column is the collection of final states
	# state_grid[i][-1].is_final = True
	
	final_state_set = set([state_grid[i][-1] for i in range(len(state_grid))])
	
	return start_state, final_state_set


def _color() -> _State:
	# Let's handle having only wild cards
	start_state = _State()
	wild_state = _State()
	wild_state.is_final = True
	wild_state.put(Color.WILD, wild_state)
	start_state.put(Color.WILD, wild_state)
	
	for color in Color:
		if color is Color.SKIP or color is Color.WILD:
			continue
		s = _State()
		s.is_final = True
		s.put(color, s)
		start_state.put(color, s)
		
		# Wild card at beginning to the color
		wild_state.put(color, s)
		# Wild cards keep us in the same state
		s.put(Color.WILD, s)
	return start_state


def _set() -> _State:
	start_state = _State()
	
	rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
	
	state_grid = [[_State() for _ in rank_list] for _ in rank_list]
	
	# A collection of wilds is a set
	wild_state = _State()
	wild_state.put(Rank.WILD, wild_state)
	start_state.put(Rank.WILD, wild_state)
	wild_state.is_final = True
	
	for r in rank_list:
		next_state = _State()
		# Next card is same rank (e.g. B3 G7)
		start_state.put(r, next_state)
		next_state.put(r, next_state)
		# Next card is wild (e.g. R7 W)
		next_state.put(Rank.WILD, next_state)
		# Wild to regular card (e.g. W Y8)
		wild_state.put(r, next_state)
		
		next_state.is_final = True
	
	return start_state


def _strictSet(size: int) -> (_State, set[_State]):
	start_state = _State()
	
	rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
	state_grid = [[_State() for _ in range(size)] for _ in rank_list]
	
	for i in range(len(rank_list)):
		r = rank_list[i]
		start_state.put(r, state_grid[i][0])
		for j in range(size - 1):
			# Next card has the same rank (e.g. R2 G2)
			state_grid[i][j].put(r, state_grid[i][j + 1])
			# Next card is wild (e.g. R2 W)
			state_grid[i][j].put(Rank.WILD, state_grid[i][j + 1])
	
	# state_grid[i][-1].is_final = True
	
	wild_list = [_State() for _ in range(size)]
	
	start_state.put(Rank.WILD, wild_list[0])
	
	for j in range(size - 1):
		wild_list[j].put(Rank.WILD, wild_list[j + 1])
		for i, r in enumerate(rank_list):
			wild_list[j].put(r, state_grid[i][j + 1])
	
	# wild_list[-1].is_final = True
	
	final_state_set = set([state_grid[i][-1] for i in range(len(state_grid))])
	final_state_set.add(wild_list[-1])
	
	return start_state, final_state_set


@dataclasses.dataclass
class RE:
	phase: str = ""
	startState: _State = dataclasses.field(default_factory=_State)
	
	def __post_init__(self):
		has_match = False
		
		m = re.fullmatch("C", self.phase)
		if m:
			self.startState = _color()
			has_match = True
		m = re.fullmatch("C(\\d+)", self.phase)
		if m:
			(self.startState, final_state_set) = _strictColor(int(m.group(1)))
			for state in final_state_set:
				state.is_final = True
			has_match = True
		m = re.fullmatch("R", self.phase)
		if m:
			self.startState = _run()
			has_match = True
		m = re.fullmatch("R(\\d+)", self.phase)
		if m:
			(self.startState, final_state_set) = _strictRun(int(m.group(1)))
			for state in final_state_set:
				state.is_final = True
			has_match = True
		
		m = re.fullmatch("S", self.phase)
		if m:
			self.startState = _set()
			has_match = True
		m = re.fullmatch("S(\\d+)", self.phase)
		if m:
			(self.startState, final_state_set) = _strictSet(int(m.group(1)))
			for state in final_state_set:
				state.is_final = True
			has_match = True
		
		m = re.fullmatch(r"([RCS]\d+\+)+[RCS]\d+", self.phase)
		if m:
			state_collection = []
			for i, phase_component in enumerate(self.phase.split("+")):
				print(i, phase_component)
				
				match phase_component[0]:
					case "R":
						(start_state, final_state_set) = _strictRun(int(phase_component[1:]))
						state_collection.append((start_state, final_state_set))
					case "C":
						(start_state, final_state_set) = _strictColor(int(phase_component[1:]))
						state_collection.append((start_state, final_state_set))
					case "S":
						(start_state, final_state_set) = _strictSet(int(phase_component[1:]))
						state_collection.append((start_state, final_state_set))
					case _:
						raise Exception(f"{phase_component} is not a valid phase component in {self.phase}!")
			
			for i in range(len(state_collection) - 1):
				empty_transition = _State()
				final_state_set = state_collection[i][1]
				for state in final_state_set:
					state.emptyTransition = empty_transition
				empty_transition.emptyTransition = state_collection[i+1][0]
			
			self.startState = state_collection[0][0]
			
			for state in state_collection[-1][1]:
				state.is_final = True
			
			has_match = True
		
		if not has_match:
			raise Exception(f"Unrecognized phase {self.phase}!")
	
	def isFullyAccepted(self, card_list):
		curr = self.startState
		for c in card_list:
			while curr.emptyTransition is not None:
				curr = curr.getNext(c)
			
			if not curr.isAccepted(c):
				return False
			curr = curr.getNext(c)
		
		return curr.is_final
	
	def to_graphviz(self):
		g = graphviz.Digraph()
		
		q = collections.deque([self.startState])
		visited = set()
		
		while q:
			curr = q.pop()
			if curr in visited:
				continue
			visited.add(curr)
			if curr is self.startState:
				g.node(str(curr._id), label="", shape="box", color="blue")
			elif curr.is_final:
				g.node(str(curr._id), label="", shape="diamond", color="green")
			else:
				g.node(str(curr._id), label="")
			for key, val in curr.rankTransition.items():
				g.edge(str(curr._id), str(val._id), label=str(key))
				q.append(val)
			for key, val in curr.colorTransition.items():
				g.edge(str(curr._id), str(val._id), label=str(key))
				q.append(val)
			for key, val in curr.cardTransition.items():
				g.edge(str(curr._id), str(val._id), label=str(key))
				q.append(val)
			if curr.emptyTransition is not None:
				g.edge(str(curr._id), str(curr.emptyTransition._id))
				q.append(curr.emptyTransition)
		
		g.render()


def main():
	rr = RE("S3+S3+R7+C4")
	print(rr.isFullyAccepted([Card.from_string(c) for c in "W B3 W R7 B7 W G2 W B4 B5 Y6 W R8 Y8 Y3 W W".split(" ")]))
	rr.to_graphviz()


if __name__ == "__main__":
	main()
