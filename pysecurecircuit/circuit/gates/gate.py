from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from cryptography.fernet import Fernet

if TYPE_CHECKING:
    from pysecurecircuit.circuit import Circuit
    from pysecurecircuit.secure_types import Wire


class Gate:
    """
    Base class representing logic gate.
    """

    name = "Gate"

    def __init__(self, circuit: Circuit, *input_wires: List[Wire]) -> None:
        """
        Initializes gate object.

        Args:
            circuit: Circuit object
            *input_wires: List of input wires
        """
        self.circuit = circuit
        self.input_wires: List[Wire] = input_wires

        # Create output wire and set gate's id to output wire's id
        self.output_wire: Wire = circuit.newWire()
        self.id = self.output_wire.id

        # Update circuit's gates and _gate_map
        self.circuit.gates.append(self)
        self.circuit._gate_map[self.id] = self

    def evaluate(self, input1: int, input2: int) -> int:
        """
        Evaluates two input bits and returns output bit.

        Returns:
            output: output bit
        """
        raise NotImplemented

    def create_grabled_truth_table(self):
        """
        Creates encrypted truth table for current gate
        """
        encrypted_table = []
        wire1, wire2 = self.input_wires

        for i in (0, 1):
            key1 = wire1.keys[i]

            for j in (0, 1):
                key2 = wire2.keys[j]

                # Evaluate input wire bits, and get corresponding key
                output_key_idx = self.evaluate(i, j)
                output_key = self.output_wire.keys[output_key_idx]

                # Encrypt output key with key2, and then encrypt it with key1
                output_key_value = str(output_key).encode()
                encrypted_table.append(
                    Fernet(key1)
                    .encrypt(Fernet(key2).encrypt(output_key_value))
                    .decode()
                )

        # Shuffle encrypted table rows
        random.shuffle(encrypted_table)
        return encrypted_table

    def __repr__(self) -> str:
        return f"Gate<{self.name}, {self.input_wires=}, {self.output_wire=}>"
