import collections
import dataclasses
import re
import uuid
from typing import Self

import graphviz

from Card import Card, Color, Rank


@dataclasses.dataclass
class _State:
    """
    This represents the nodes used in a regular expression automata
    """
    
    # Indicates if this is a final node in the graph
    # This is used to indicate that we have accepted the sequence of cards
    is_final: bool = False
    
    # Used to make the states hashable
    _id: int = dataclasses.field(default_factory=lambda: uuid.uuid4().int)
    # Traverses based off of a given card
    cardTransition: dict[Card, Self] = dataclasses.field(default_factory=dict)
    # Traverses based off of a given card rank
    rankTransition: dict[Rank, Self] = dataclasses.field(default_factory=dict)
    # Traverses based off of a given card color
    colorTransition: dict[Color, Self] = dataclasses.field(default_factory=dict)
    
    # Because phases can have multiple components (e.g. S3+S3), we will need empty nodes which serve no purpose other
    # than to connect two RE graphs We will have a transition that doesn't require a card, color, or rank
    emptyTransition: Self = None
    
    def put(self, item: Card | Rank | Color, next_state: Self):
        """
        This indicates to which node we'll traverse based on a card, color, or rank
        
        :param item: The card, color, or rank that indicates where to transition
        :type item: Card | Rank | Color
        :param next_state: The state to which we'll transition
        """
        if isinstance(item, Card):
            self.cardTransition[item] = next_state
        elif isinstance(item, Rank):
            self.rankTransition[item] = next_state
        elif isinstance(item, Color):
            self.colorTransition[item] = next_state
        else:
            raise Exception(f"Cannot insert {item} because it's of type {type(item)}")
    
    def isAccepted(self, c: Card) -> bool:
        """
        Indicates if the card will result in a transition
        
        :param c: The card to test
        :type c: Card
        :return: Whether the card will result in a transition
        :rtype bool
        """
        if self.emptyTransition is not None:
            return True
        return (
            (c in self.cardTransition)
            or (c.color in self.colorTransition)
            or (c.rank in self.rankTransition)
        )
    
    def getNext(self, item: Card) -> Self:
        """
        Get the state to transition based off of a card, color, or rank
        
        :param item: A card, color, or rank that indicates where to transition
        :type item: Card | Rank | Color
        :return: The state to transition based on item
        :rtype: _State
        :raises Exception: if item does not lead us to a new state
        """
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
    """
    Generate a RE graph that can be used to determine if a sequence of cards is a run
    A run is a sequence of cards whose ranks are in strictly increasing sequential order
    One example is R3, B4, Y5
    R3, B3, Y3 is not a run
    R5, B4, Y3 is not a run
    Also note that R11, B12, Y1, G2 is not a run
    
    :return: The initial state to the RE graph
    :rtype: _State
    """
    start_state = _State()
    # List the ranks in sequential order
    rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
    
    # Record the states and transitions for regular cards
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
    start_state.put(Rank.WILD, wild_state[0])
    
    for j in range(len(wild_state) - 1):
        # Chain the wilds together since a collection of wilds is a run
        wild_state[j].put(Rank.WILD, wild_state[j + 1])
        wild_state[j].is_final = True
    wild_state[-1].is_final = True
    
    for i in range(len(state_grid)):
        for j in range(len(state_grid[i]) - 1):
            # Wild to next card (e.g. W R3)
            wild_state[j].put(rank_list[i + j + 1], state_grid[i][j + 1])
    
    return start_state


def _strictRun(size: int) -> (_State, set[_State]):
    """
    Generate a RE graph that can be used to determine if a sequence of cards is a run of a specified size
    We return the start state and a set of states that could be the final states
    We don't make them final because of phases with multiple components mean that we will have to continue to transition to another graph
    
    :param size: the number of desired cards in the run
    :type size: int
    :return: The initial state to the RE graph and a set of states that could be considered final
    :rtype: tuple[_State, set[_State]]
    """
    
    if size < 1 or size > 12:
        raise Exception(f"Invalid size {size}. Must be between 1 and 12 inclusive!")
    
    start_state = _State()
    rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
    
    # Generate the graph for regular cards
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
    
    # Need a separate collection of wilds
    wild_state = [_State() for _ in range(size)]
    start_state.put(Rank.WILD, wild_state[0])
    for j in range(size - 1):
        # Chain the wilds together since a collection of wilds is a run
        wild_state[j].put(Rank.WILD, wild_state[j + 1])
        for i in range(len(state_grid)):
            # Wild to next card (e.g. W R3)
            wild_state[j].put(rank_list[i + j + 1], state_grid[i][j + 1])
    
    final_state_set = set([state_grid[i][-1] for i in range(len(state_grid))])
    final_state_set.add(wild_state[-1])
    
    return start_state, final_state_set


def _color() -> _State:
    """
    Generate a RE graph that can be used to determine if a sequence of cards consists of only one color
    One example is R3, R4, R3, R7
    
    :return: The initial state to the RE graph
    :rtype: _State
    """
    
    # Let's handle having only wild cards
    start_state = _State()
    wild_state = _State()
    wild_state.is_final = True
    wild_state.put(Color.WILD, wild_state)
    start_state.put(Color.WILD, wild_state)
    
    # Now, we'll handle regular cards
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


def _strictColor(size: int) -> (_State, set[_State]):
    """
    Generate a RE graph that can be used to determine if a sequence of cards consists of only one color
    However, the cardinality of the cards must be the same as an inputted value
    We don't make them final because of phases with multiple components mean that we will have to continue to transition to another graph
    
    :param size: the number of desired cards in the phase component
    :type size: int
    :return: The initial state to the RE graph and a set of states that could be considered final
    :rtype: tuple[_State, set[_State]]
    """
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
    
    final_state_set = set([state_grid[i][-1] for i in range(len(state_grid))])
    
    return start_state, final_state_set


def _set() -> _State:
    """
    Generate a RE graph that can be used to determine if a sequence of cards consists of only one rank
    One example is R3, B3, Y3
    
    :return: The initial state to the RE graph
    :rtype: _State
    """
    start_state = _State()
    
    rank_list = [r for r in Rank if (r is not Rank.WILD and r is not Rank.SKIP)]
    
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
    """
    Generate a RE graph that can be used to determine if a sequence of cards consists of only one rank However,
    the cardinality of the cards must be the same as an inputted value We don't make them final because of phases
    with multiple components mean that we will have to continue to transition to another graph
    
    :param size: the number of desired cards in the set
    :type size: int
    :return: The initial state to the RE graph and a set of states that could be considered final
    :rtype: tuple[_State, set[_State]]
    """
    start_state = _State()
    
    # Generate the graph for regular cards
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
    
    # Add in the wild cards
    wild_list = [_State() for _ in range(size)]
    
    start_state.put(Rank.WILD, wild_list[0])
    
    for j in range(size - 1):
        wild_list[j].put(Rank.WILD, wild_list[j + 1])
        for i, r in enumerate(rank_list):
            wild_list[j].put(r, state_grid[i][j + 1])
    
    # Record our final states
    final_state_set = set([state_grid[i][-1] for i in range(len(state_grid))])
    final_state_set.add(wild_list[-1])
    
    return start_state, final_state_set


@dataclasses.dataclass
class RE:
    """
    This is a regular expression that can determine if a collection of cards matches a given phase
    """
    
    # The phase. Must be in the format [CRS](\d+)?(\+[CRS](\d+)?)+
    # Valid examples include C, R, S, R7, C4, S8, S3+S3, R7+C4, C2+C4
    phase: str = ""
    # The start state for the graph
    startState: _State = dataclasses.field(default_factory=_State)
    len: int = 0
    
    def __post_init__(self):
        """
        Create the graph for validation
        """
        
        # Is the inputted phase a valid phase
        has_match = False
        
        # These are the simple cases. Just call one of the functions above to generate run, set, or color graphs
        m = re.fullmatch("C", self.phase)
        if m:
            self.startState = _color()
            has_match = True
        m = re.fullmatch("C(\\d+)", self.phase)
        if m:
            self.len = int(m.group(1))
            (self.startState, final_state_set) = _strictColor(self.len)
            for state in final_state_set:
                state.is_final = True
            has_match = True
        m = re.fullmatch("R", self.phase)
        if m:
            self.startState = _run()
            has_match = True
        m = re.fullmatch("R(\\d+)", self.phase)
        if m:
            self.len = int(m.group(1))
            (self.startState, final_state_set) = _strictRun(self.len)
            for state in final_state_set:
                state.is_final = True
            has_match = True
        
        m = re.fullmatch("S", self.phase)
        if m:
            self.startState = _set()
            has_match = True
        m = re.fullmatch("S(\\d+)", self.phase)
        if m:
            self.len = int(m.group(1))
            (self.startState, final_state_set) = _strictSet(self.len)
            for state in final_state_set:
                state.is_final = True
            has_match = True
        
        # Multi-component phases
        m = re.fullmatch(r"([RCS]\d+\+)+[RCS]\d+", self.phase)
        if m:
            state_collection = []
            # Get each start and final states
            for i, phase_component in enumerate(self.phase.split("+")):
                
                match phase_component[0]:
                    case "R":
                        self.len += int(phase_component[1:])
                        (start_state, final_state_set) = _strictRun(int(phase_component[1:]))
                        state_collection.append((start_state, final_state_set))
                    case "C":
                        self.len += int(phase_component[1:])
                        (start_state, final_state_set) = _strictColor(int(phase_component[1:]))
                        state_collection.append((start_state, final_state_set))
                    case "S":
                        self.len += int(phase_component[1:])
                        (start_state, final_state_set) = _strictSet(int(phase_component[1:]))
                        state_collection.append((start_state, final_state_set))
                    case _:
                        raise Exception(f"{phase_component} is not a valid phase component in {self.phase}!")
            
            # Connect the components using empty transitions
            for i in range(len(state_collection) - 1):
                empty_transition = _State()
                final_state_set = state_collection[i][1]
                for state in final_state_set:
                    state.emptyTransition = empty_transition
                empty_transition.emptyTransition = state_collection[i + 1][0]
            
            # Record the very first start state
            self.startState = state_collection[0][0]
            
            # Make the very last final states final
            for state in state_collection[-1][1]:
                state.is_final = True
            
            has_match = True
        
        # What has been inputted is not a valid phase
        if not has_match:
            raise Exception(f"Unrecognized phase {self.phase}!")
    
    def isFullyAccepted(self, card_list) -> bool:
        """
        Determines if a sequence of cards matches the phase exactly as stated. It must match the exact order of the
        components (e.g. R1,G2,Y3,R7,B7,Y7 does not match S3+R3 but does match R3+S3) and it must have exactly the
        number of cards asked by the phase (e.g. R1, B2, Y3, G4 does not match R3 but does match R4)
        
        :param card_list: the sequence of card to test
        :return: if the cards match the phase
        :rtype: bool
        """
        curr = self.startState
        for c in card_list:
            while curr.emptyTransition is not None:
                curr = curr.getNext(c)
            
            if not curr.isAccepted(c):
                return False
            curr = curr.getNext(c)
        
        return curr.is_final
    
    def to_graphviz(self):
        """
        Outputs the graph to pdf format for visualization
        """
        g = graphviz.Digraph()
        
        q = collections.deque([self.startState])
        visited = set()
        
        while q:
            curr = q.pop()
            if curr in visited:
                continue
            visited.add(curr)
            if curr is self.startState:
                g.node(str(hash(curr)), label="", shape="box", color="blue")
            elif curr.is_final:
                g.node(str(hash(curr)), label="", shape="diamond", color="green")
            else:
                g.node(str(hash(curr)), label="")
            for key, val in curr.rankTransition.items():
                g.edge(str(hash(curr)), str(hash(val)), label=str(key))
                q.append(val)
            for key, val in curr.colorTransition.items():
                g.edge(str(hash(curr)), str(hash(val)), label=str(key))
                q.append(val)
            for key, val in curr.cardTransition.items():
                g.edge(str(hash(curr)), str(hash(val)), label=str(key))
                q.append(val)
            if curr.emptyTransition is not None:
                g.edge(str(hash(curr)), str(hash(curr.emptyTransition)))
                q.append(curr.emptyTransition)
        
        g.render()


def main():
    rr = RE("S3+S3+R7+C4")
    print(rr.isFullyAccepted([Card.from_string(c) for c in "W B3 W R7 B7 W G2 W B4 B5 Y6 W R8 Y8 Y3 W W".split(" ")]))
    rr.to_graphviz()


if __name__ == "__main__":
    main()
