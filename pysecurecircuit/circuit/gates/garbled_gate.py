from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

from cryptography.fernet import Fernet

if TYPE_CHECKING:
    from pysecurecircuit.circuit.garble_key import GarbledKey


class GarbledGate:
    """
    Class representing a gate in a garbled circuit.
    """

    def __init__(self, id: int, garbled_table: List[str]) -> None:
        """
        Initialize a GarbledGate object with the given ID and garbled table.

        Args:
            id: the ID of the gate
            garbled_table: the garbled truth table of the gate
        """
        self.id: int = id
        self.input_keys: List[GarbledKey] = []
        self.output_key: bytes = None
        self.garbled_table: List[bytes] = [s.encode() for s in garbled_table]

    def evaluate(self):
        """
        Evaluate the gate by decrypting the garbled table using the input keys.
        Set the output key to the result of the decryption.
        """
        key0, key1 = [input_key.key.encode() for input_key in self.input_keys]

        for row in self.garbled_table:
            try:
                msg1 = Fernet(key0).decrypt(row)
                msg = Fernet(key1).decrypt(msg1)

                self.output_key = msg

                return
            except:
                continue

        raise Exception("Invalid keys, could not decrypt the gate")

    def __repr__(self) -> str:
        return f"GarbledGate({self.id}, {self.garbled_table=})"
