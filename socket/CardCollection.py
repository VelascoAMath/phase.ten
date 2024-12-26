import json
from typing import Self

from Card import Card, Color, Rank


class CardCollection(list):
    
    def __eq__(self, other):
        if isinstance(other, CardCollection):
            if len(self) != len(other):
                return False
            
            for i in range(len(self)):
                if self[i] != other[i]:
                    return False
            return True
            
        else:
            raise Exception(f"Cannot compare CardCollection with item of type {type(other)}!")
    
    def __str__(self):
        return f"{[str(c) for c in self]}"
    
    def to_json(self):
        return json.dumps(self.to_json_dict())
    
    def to_json_dict(self):
        return [x.to_json_dict() for x in self]
    
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return CardCollection.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data):
        return CardCollection([Card.fromJSONDict(card) for card in data])
    
    @staticmethod
    def getNewDeck() -> Self:
        deck = CardCollection()
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
        return deck


def main():
    deck = CardCollection.getNewDeck()
    
    print(deck)
    print(deck == CardCollection.from_json(deck.to_json()))


# print(CardCollection.exists(deck.id))

# print(deck.all())

# print(CardCollection.get_by_id(deck.id))


# print(deck)
#
# print(deck == from_json(deck.toJSON()))


if __name__ == '__main__':
    main()
