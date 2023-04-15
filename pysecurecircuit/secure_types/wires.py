from __future__ import annotations

from typing import TYPE_CHECKING, List

from pysecurecircuit.secure_types import Wire

if TYPE_CHECKING:
    from pysecurecircuit.circuit import Circuit


class Wires:
    kind = "wires"

    def __init__(
        self, circuit: Circuit, num_wires: int, wires: List[Wire] = None
    ) -> None:
        """
        Initializes Wires object.
        If wires are provided, they will be grouped in current object,
        else new wires will be added to the circuit.

        Args:
            circuit: Circuit object
            num_wires: Number of wires to create
            wires (Optional): List of existing wires to group in Wires object
        """
        if num_wires <= 0:
            raise Exception("Invalid wires")

        self.circuit = circuit
        self.num_wires = num_wires

        # Initially set party id to -1 which indicates that this
        # Wires object is internal wires object, and it is depended on
        # inout wires.
        # When current object is assigned as input to any party, this value
        # will be changed.
        self.party_id = -1

        # Create new wires if wires is not provided
        if wires is None:
            self.wires = [circuit.newWire() for _ in range(self.num_wires)]
        else:
            self.wires = wires

    def set_as_input_wires(self, party_id: int) -> None:
        """
        Set this object with all Wire objects as input wire of given party.

        Args:
            party_id: ID of party
        """
        self.party_id = party_id

        for wire in self.wires:
            wire.set_as_input_wire(party_id)

    def __repr__(self) -> str:
        return f"Wires<{self.wires}>"

    def set_output(self):
        for wire in self.wires:
            wire.set_output()

    def set_value(self, value: int) -> None:
        if value < 0:
            raise NotImplemented

        bit_str = bin(value)[2:]

        if len(bit_str) > self.num_wires:
            raise Exception("Integer overflow")
        elif len(bit_str) < self.num_wires:
            bit_str = "0" * (self.num_wires - len(bit_str)) + bit_str

        for i in range(self.num_wires):
            self.wires[i].set_value(int(bit_str[i]))

    def __eq__(self, obj: Wires) -> Wire:
        # if self.num_wires != obj.num_wires:
        #     raise Exception("Invalid number of wires")

        # last_output: Wire = self.wires[0] == obj.wires[0]

        # for i in range(1, len(self.wires)):
        #     last_output = last_output == (self.wires[i] == obj.wires[i])

        # return last_output
        if self.num_wires != obj.num_wires:
            raise Exception("Invalid number of wires")

        xnor_gates: List[Wire] = [
            self.wires[i] == obj.wires[i]
            for i in range(len(self.wires))
        ]

        output_wire: Wire = xnor_gates[0] & xnor_gates[1]

        for i in range(2, len(xnor_gates)):
            output_wire = output_wire & xnor_gates[i]

        return output_wire

    def __add__(self, obj: Wires) -> Wires:
        raise NotImplemented

    def __gt__(self, obj: Wires) -> Wires:
        raise NotImplemented

    def __and__(self, __value: Wire | Wires) -> Wires:
        new_wires: List[Wire] = None
        if isinstance(__value, Wire):
            new_wires = []

            for i in range(len(self.wires)):
                new_wire = self.circuit._and(self.wires[i], __value)
                new_wires.append(new_wire)

        elif isinstance(__value, Wires):
            if len(self.wires) != len(__value.wires):
                raise Exception("Length of wires in both values are not equal")

            new_wires = []

            for i in range(len(self.wires)):
                new_wire = self.circuit._and(self.wires[i], __value.wires[i])

                new_wires.append(new_wire)
        else:
            raise NotImplemented

        return Wires(circuit=self.circuit, num_wires=self.num_wires, wires=new_wires)

    def __or__(self, __value: Wire | Wires) -> Wires:
        new_wires: List[Wire] = None
        if isinstance(__value, Wire):
            new_wires = []

            for i in range(len(self.wires)):
                new_wire = self.circuit._or(self.wires[i], __value)
                new_wires.append(new_wire)
        elif isinstance(__value, Wires):
            if len(self.wires) != len(__value.wires):
                raise Exception("Length of wires in both values are not equal")

            new_wires = []

            for i in range(len(self.wires)):
                new_wire = self.circuit._or(self.wires[i], __value.wires[i])

                new_wires.append(new_wire)
        else:
            raise NotImplemented

        return Wires(circuit=self.circuit, num_wires=self.num_wires, wires=new_wires)
