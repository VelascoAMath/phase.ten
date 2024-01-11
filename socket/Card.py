import dataclasses
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

    # def __str__(self):
    # 	return self.__repr__()

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


@dataclasses.dataclass(order=True, frozen=True)
class Card:
    color: Color = dataclasses.field(default_factory=lambda: Color.WILD)
    rank: Rank = dataclasses.field(default_factory=lambda: Rank.WILD)

    def __post_init__(self):
        if self.color == Color.WILD and self.rank != Rank.WILD:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

        if self.color != Color.WILD and self.rank == Rank.WILD:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

        if self.color == Color.SKIP and self.rank != Rank.SKIP:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

        if self.color != Color.SKIP and self.rank == Rank.SKIP:
            raise Exception(
                f"Cannot create a card with color {self.color} and rank {self.rank}!"
            )

    def __str__(self):
        if self.color == Color.WILD and self.rank == Rank.WILD:
            return "W"
        if self.color == Color.SKIP and self.rank == Rank.SKIP:
            return "S"
        return f"{self.color}{self.rank}"


def main():
    for rank in Rank:
        for color in Color:
            c = Card(color, rank)
            print(c)


if __name__ == "__main__":
    main()
