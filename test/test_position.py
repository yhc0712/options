import unittest
from contract import Contract, Call, Put
from position import Position


class TestPosition(unittest.TestCase):
    def setUp(self):
        # Create a Position object
        self.position = Position()
        self.position_2 = Position()
        # Create a Contract object
        self.contract = Call(strike=16500, actual_premium=50)
        self.position_2.add(self.contract)

    def test_add_position(self):
        # Add the Contract to the Position
        self.position.add(self.contract)

        # Check that the Contract was correctly added to the Position
        self.assertEqual(self.position.Position, [self.contract])

    def test_close_position(self):
        # Close the Contract
        self.position_2.close(self.contract)

        # Check that the Contract was correctly removed from the Position
        self.assertEqual(self.position_2.Position, [])


if __name__ == "__main__":
    unittest.main()
