import unittest

from Card import Card
from RE import RE


class TestRE(unittest.TestCase):
	def test_strict_run(self):
		rr = RE("R4")
		accepted_list = ["R1 R2 R3 R4", "W W W R7", "W W W W", "B1 G2 Y3 R4", "W W W W"]
		for phase in accepted_list:
			deck = [Card.from_string(c) for c in phase.split(" ")]
			self.assertTrue(rr.isFullyAccepted(deck))
		
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
		self.assertTrue(
			rr.isFullyAccepted([Card.from_string(c) for c in "W B3 W R7 B7 W G2 W B4 B5 Y6 W R8 Y8 Y3 W W".split(" ")]))


if __name__ == "__main__":
	unittest.main()
