import dataclasses
import json
import re
from enum import Enum


@dataclasses.dataclass
class Rank(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    WILD = 11
    SKIP = 12

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
    	return self.__repr__()

    def __repr__(self):
        match self.name:
            case "ONE":
                return "1"
            case "TWO":
                return "2"
            case "THREE":
                return "3"
            case "FOUR":
                return "4"
            case "FIVE":
                return "5"
            case "SIX":
                return "6"
            case "SEVEN":
                return "7"
            case "EIGHT":
                return "8"
            case "NINE":
                return "9"
            case "TEN":
                return "10"
            case "WILD":
                return "W"
            case "SKIP":
                return "S"
            case "JACK":
                return "J"
            case "QUEEN":
                return "Q"
            case "KING":
                return "K"
            case _:
                return self.name
        
    @staticmethod
    def fromJSON(data):
        match data:
            case "1":
                return Rank.ONE
            case "2":
                return Rank.TWO
            case "3":
                return Rank.THREE
            case "4":
                return Rank.FOUR
            case "5":
                return Rank.FIVE
            case "6":
                return Rank.SIX
            case "7":
                return Rank.SEVEN
            case "8":
                return Rank.EIGHT
            case "9":
                return Rank.NINE
            case "10":
                return Rank.TEN
            case "W":
                return Rank.WILD
            case "S":
                return Rank.SKIP
            case _:
                raise Exception(f"{data} is not a valid rank!")


@dataclasses.dataclass
class Color(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    SKIP = 4
    WILD = 5

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        match self.name:
            case "RED":
                return "R"
            case "BLUE":
                return "B"
            case "GREEN":
                return "G"
            case "YELLOW":
                return "Y"
            case "WILD":
                return "W"
            case "SKIP":
                return "S"
            case _:
                return self.name
    
    @staticmethod
    def fromJSON(data):
        match data:
            case "R":
                return Color.RED
            case "G":
                return Color.GREEN
            case "Y":
                return Color.YELLOW
            case "B":
                return Color.BLUE
            case "S":
                return Color.SKIP
            case "W":
                return Color.WILD
            case _:
                raise Exception(f"{data} is not a valid color!")
        
    
    

@dataclasses.dataclass(order=True, frozen=True)
class Card:
    color: Color = dataclasses.field(default_factory=lambda: Color.WILD)
    rank: Rank = dataclasses.field(default_factory=lambda: Rank.WILD)

    def __post_init__(self):
        if self.color is Color.WILD and self.rank is not Rank.WILD:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

        if self.color is not Color.WILD and self.rank is Rank.WILD:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

        if self.color is Color.SKIP and self.rank is not Rank.SKIP:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

        if self.color is not Color.SKIP and self.rank is Rank.SKIP:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

    def __str__(self):
        if self.color is Color.WILD and self.rank is Rank.WILD:
            return "W"
        if self.color is Color.SKIP and self.rank is Rank.SKIP:
            return "S"

        return f"{self.color}{self.rank}"

    def toJSON(self):
        return json.dumps({"color": str(self.color), "rank": str(self.rank)})
    
    @staticmethod
    def fromJSON(data):
        data = json.loads(data)
        
        return Card(Color.fromJSON(data["color"]), Rank.fromJSON(data["rank"]))
    
    @staticmethod
    def from_string(data):
        
        # Cards like R9, G8, B2, etc.
        m = re.fullmatch("([RGYB])([0-9])", data)
        if m:
            return Card(Color.fromJSON(m.group(1)), Rank.fromJSON(m.group(2)))
        
        # Cards with rank 10
        m = re.fullmatch("([RGYB])10", data)
        if m:
            return Card(Color.fromJSON(m.group(1)), Rank.TEN)
        
            
        match data:
            case "S":
                return Card(Color.SKIP, Rank.SKIP)
            case "W":
                return Card(Color.WILD, Rank.WILD)
            case "_":
                raise Exception(f"{data} is not a valid card!")

def main():
    for rank in Rank:
        for color in Color:
            if rank is Rank.WILD and color is not Color.WILD:
                continue
            if rank is Rank.SKIP and color is not Color.SKIP:
                continue
            if color is Color.WILD and rank is not Rank.WILD:
                continue
            if color is Color.SKIP and rank is not Rank.SKIP:
                continue
            c = Card(color, rank)
            print(c)
            print(c.toJSON())
            print(Card.fromJSON(c.toJSON()))
            print(Card.from_string(str(c)))
            print()


if __name__ == "__main__":
    main()
