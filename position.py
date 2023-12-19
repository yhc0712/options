import numpy as np
import pandas as pd
from contract import Contract, Call, Put
from dataclasses import dataclass, field
from margin_data import Txo_A, Txo_B, Tx, Mtx


@dataclass
class Position:
    """
    Represents a position in a trading system.

    Attributes:
        _Position (list): A list of contracts representing the position.

    Methods:
        add(contract: Contract): Adds a contract to the position.
        close(contract: Contract): Closes a contract from the position.
    """

    _Position: list = field(default_factory=list)

    @property
    def Position(self):
        return self._Position

    def _save_position(self):
        # TODO save the position after adding or closing a contract
        pass

    def add(self, contract: Contract):
        self._Position.append(contract)
        # TODO save the position after adding a contract

    def close(self, contract: Contract):
        self._Position.remove(contract)
        # TODO save the position after closing a contract

    def update(self, current_spot):
        for contract in self._Position:
            # TODO save original greeks in a dict
            contract.simulation_spot = current_spot
            # TODO convert the contract objects to a dataframe
            # TODO calculate Cash Delta and Cash Gamma
            # TODO calculate margin

    def simulation(self, return_upper: float = 0.1, return_lower: float = -0.1):
        # TODO pending
        pass


if __name__ == "__main__":
    pos = Position()
    call = Call(strike=17600, actual_premium=14)
    old_delta = call.delta

    pos.add(call)
    print(pos.Position)
    pos.update(16000)
    print(pos.Position)
    new_delta = call.delta
    print(f"Old delta: {old_delta}; New delta: {new_delta}")
