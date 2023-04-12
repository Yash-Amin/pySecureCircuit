from __future__ import annotations

from typing import TYPE_CHECKING

from cryptography.fernet import Fernet

if TYPE_CHECKING:
    from pysecurecircuit.circuit import Circuit


class Wire:
    kind = "wire"

    def __init__(self, circuit: Circuit, wire_id: int, bit_value: int = None) -> None:
        """
        Initialize Wire object.

        Args:
            circuit: Circuit object
            wire_id: Wire id
            bit_value (optional): Bit value of current wire
        """
        self.id = wire_id
        self.circuit = circuit
        self.bit_value = None

        # Initially set party id to -1 which indicates that this
        # Wires object is internal wires object, and it is depended on
        # inout wires.
        # When current object is assigned as input to any party, this value
        # will be changed.
        self.party_id = -1

        self.is_input_wire = False
        self.is_output_wire = False

        # Generate keys for each label
        # When wire is marked as output wire, keys will be set to (0, 1)
        self.keys = (
            Fernet.generate_key().decode(),
            Fernet.generate_key().decode(),
        )

        if bit_value is not None:
            self.set_value(bit_value)

    def set_value(self, bit_value: int):
        self.bit_value = bit_value

        if not self.is_input_wire:
            self.circuit.const_keys[self.id] = self.keys[bit_value]

    def set_as_input_wire(self, party_id: int) -> None:
        """
        Set this object as input wire of given party.

        Args:
            party_id: ID of party
        """
        # When a wire is marked as input wire, then remove it from constant keys
        if self.id in self.circuit.const_keys:
            self.circuit.const_keys.pop(self.id)

        self.party_id = party_id
        self.is_input_wire = True

    def set_output(self):
        """
        Set this object as output wire.

        TODO: Output wire must not be used as input to other gates
        """
        # Set keys to (0, 1) as this is output wire
        self.keys = (0, 1)
        self.is_output_wire = True

    def __eq__(self, obj: Wire) -> Wire:
        return self.circuit._xnor(self, obj)

    def __and__(self, obj: Wire) -> Wire:
        return self.circuit._and(self, obj)

    def __or__(self, obj: Wire) -> Wire:
        return self.circuit._or(self, obj)

    def __xor__(self, obj: Wire) -> Wire:
        return self.circuit._xor(self, obj)

    def __xnor__(self, obj: Wire) -> Wire:
        return self.circuit._xnor(self, obj)

    def __not__(self) -> Wire:
        return self.circuit._xor(self, self.circuit.newWire(1))

    def __gt__(self, obj: Wire) -> Wire:
        return self.circuit._and(self, obj.__not__())

    def __lt__(self, obj: Wire) -> Wire:
        return self.circuit._and(self.__not__(), obj)

    def __ge__(self, obj: Wire) -> Wire:
        return (self < obj).__not__()

    def __le__(self, obj: Wire) -> Wire:
        return obj >= self

    def __repr__(self) -> str:
        return f"Wire<{self.id}, {self.is_input_wire=}, {self.is_output_wire=}>"
