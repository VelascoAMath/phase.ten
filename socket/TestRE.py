import itertools
import random
import unittest

import more_itertools

from Card import Card
from CardCollection import CardCollection
from RE import RE


class TestRE(unittest.TestCase):
    
    def setUp(self):
        random.seed(2024)
    
    def test_strict_run(self):
        rr = RE("R4")
        accepted_list = ["R1 R2 R3 R4", "W W W R7", "W W W W", "B1 G2 Y3 R4", "W W W W"]
        for phase in accepted_list:
            deck = CardCollection([Card.from_string(c) for c in phase.split(" ")])
            self.assertTrue(rr.isFullyAccepted(deck))
            self.assertTrue(rr.isSubsetAccepted(deck)[0])
        
        not_accepted_list = [
            "R1 B1",
            "R1 R2 R3 R4 R5",
            "R2 W R5",
            "R4 R3",
            "W W W W W",
            "W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isFullyAccepted(deck))
        
        
        not_accepted_list = [
            "R1 B1",
            "R2 W R5",
            "R4 R3",
            "W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isSubsetAccepted(deck)[0])
    
    def test_run(self):
        rr = RE("R")
        accepted_list = [
            "Y10",
            "W",
            "R1 R2 R3 R4",
            "W W W R7",
            "R7 W W W",
            "W W W W",
            "B1 G2 Y3 R4",
            "W W W W W W W W W W W W",
        ]
        for phase in accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertTrue(rr.isFullyAccepted(deck))
            self.assertTrue(rr.isSubsetAccepted(deck)[0])
        
        not_accepted_list = [
            "R1 B1",
            "R1 R2 R3 R5 R5",
            "R2 W R5",
            "R4 R3",
            "W W W W W W W W W W W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isFullyAccepted(deck))
    
    def test_strict_set(self):
        rr = RE("S4")
        accepted_list = ["R1 B1 G1 Y1", "W W W R7", "W W W W", "R1 R1 R1 R1", "W W W W"]
        for phase in accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertTrue(rr.isFullyAccepted(deck))
        
        not_accepted_list = [
            "R1 B1",
            "R1 R1 R1 R1 R1",
            "R2 W R3",
            "R4 R3",
            "W W W W W",
            "W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isFullyAccepted(deck))
        
        not_accepted_list = [
            "R1 B1",
            "R2 W R3",
            "R4 R3",
            "W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isSubsetAccepted(deck)[0])
    
    def test_set(self):
        rr = RE("S")
        accepted_list = [
            "Y10",
            "W",
            "R1 Y1 G1 B1",
            "W W W R7",
            "R7 W W W",
            "W W W W",
            "B1 W W Y1",
            "W W W W W W W W W W W W",
        ]
        for phase in accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertTrue(rr.isFullyAccepted(deck))
        
        not_accepted_list = [
            "R1 R2",
            "R1 R1 Y1 R5 B1",
            "R2 W R5",
            "R4 R3"
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isFullyAccepted(deck))
    
    def test_strict_color(self):
        rr = RE("C4")
        accepted_list = ["R1 R2 R11 R3", "W W W R7", "W W W W", "R1 R1 R1 R1", "W W W W"]
        for phase in accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertTrue(rr.isFullyAccepted(deck))
            self.assertTrue(rr.isSubsetAccepted(deck)[0])
        
        not_accepted_list = [
            "R1 B1",
            "R1 R1 R1 R1 Y1",
            "R2 W B3",
            "R4 B3",
            "W W W W W",
            "W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isFullyAccepted(deck))
            
        not_accepted_list = [
            "R1 B1",
            "R2 W B3",
            "R4 B3",
            "W W W",
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isSubsetAccepted(deck)[0])
    
    def test_color(self):
        rr = RE("C")
        accepted_list = [
            "Y10",
            "W",
            "R1 R11 R1 R12",
            "W W W R7",
            "R7 W W W",
            "W W W W",
            "B1 W W B1",
            "W W W W W W W W W W W W",
        ]
        for phase in accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertTrue(rr.isFullyAccepted(deck))
        
        not_accepted_list = [
            "R1 B1",
            "R1 R1 R1 B1 R1",
            "R2 W B2",
            "R4 B3"
        ]
        for phase in not_accepted_list:
            deck = [Card.from_string(c) for c in phase.split(" ")]
            self.assertFalse(rr.isFullyAccepted(deck))
    
    def test_complex_component(self):
        rr = RE("S3+S3+R7+C4")
        deck = CardCollection([Card.from_string(c) for c in "W B3 W R7 B7 W G2 W B4 B5 Y6 W R8 Y8 Y3 W W".split(" ")])
        self.assertTrue(rr.isFullyAccepted(deck))
        random.shuffle(deck)
        self.assertTrue(rr.isSubsetAccepted(deck)[0])

        self.assertEqual(rr.len, 17)

        deck = CardCollection(
            [Card.from_string(c) for c in "R3 B3 Y3 R7 B7 G7 G2 Y3 B4 B5 Y6 R7 R8 Y8 Y3 Y11 Y4".split(" ")]
        )
        self.assertTrue(rr.isFullyAccepted(deck))
        random.shuffle(deck)
        self.assertTrue(rr.isSubsetAccepted(deck)[0])

        deck = CardCollection(
            [Card.from_string(c) for c in "R2 B3 Y3 R7 B7 G7 G2 Y3 B4 B5 Y6 R7 R8 Y8 Y3 Y11 Y4".split(" ")]
        )
        self.assertFalse(rr.isFullyAccepted(deck))
        random.shuffle(deck)
        self.assertFalse(rr.isSubsetAccepted(deck)[0])
    
    def test_score(self):
        rr = RE("R10")

        for i, shuffled_card in enumerate(more_itertools.powerset([Card.from_string(c) for c in "R1 R3 B4 G5".split(" ")])):
            for cards in itertools.permutations(shuffled_card):
                self.assertEqual(rr.score(CardCollection(cards)), 10 - len(cards))

        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R1 R3 B4 G5".split(" ")])), 6)

        rr = RE("S3")
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R3 G3 B7".split(" ")])), 1)

        rr = RE("C7")
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R1 R2 R3 B1 B2 B3 B4".split(" ")])), 3)

        rr = RE("C7")
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R1 R2 R3 R4 R5 B1 B2 B3 B4 B5 B6".split(" ")])), 1)
        rr = RE("S3")
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R1 B1".split(" ")])), 1)

        rr = RE("R4")
        rr.to_graphviz()
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R12".split(" ")])), 3)
        
        rr = RE("R4+S4")
        rr.to_graphviz()
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R2 R3 R4 R5 R6 B2 G2 Y2".split(" ")])), 0)
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R6 R5 R4 R3 R2 Y2 G2 B2".split(" ")])), 0)
        self.assertEqual(rr.score(CardCollection([Card.from_string(c) for c in "R6".split(" ")])), 7)


if __name__ == "__main__":
    unittest.main()
