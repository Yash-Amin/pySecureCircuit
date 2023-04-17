from __future__ import annotations

from typing import Dict, List, Tuple

from pysecurecircuit.circuit.circuit_input import CircuitInput
from pysecurecircuit.circuit.circuit_output import CircuitOutput
from pysecurecircuit.circuit.gates import AndGate, Gate, OrGate, XnorGate, XorGate
from pysecurecircuit.secure_types import Wire, Wires, _SecureInt


class Circuit:
    """
    Represents boolean circuit.
    """

    def __init__(self, name: str, num_parties: int) -> None:
        """
        Initializes a new Circuit object.

        Args:
            name (str): Name of the circuit
            num_parties (int): The number of parties involved in the computation.

        Raises:
            Exception: If the number of parties is less than or equal to 1.
            NotImplemented: If the number of parties is greater than 2.
        """
        if num_parties <= 1:
            raise Exception("Number of parties must be greater than 1")
        elif num_parties > 2:
            raise NotImplemented

        self.name = name
        self.num_parties = num_parties

        self.gates: List[Gate] = []
        self.wires: List[Wire] = []
        self._gate_map: Dict[int, Gate] = {}
        self._wire_map: Dict[int, Wire] = {}

        # To store keys for constant wires
        self.const_keys: Dict[int, str] = {}

        # List of outputs that must be evaluated
        self.outputs: List[CircuitOutput] = []

        # Mapping of party-id to their CircuitInput objects
        self.inputs: Dict[int, List[CircuitInput]] = {
            i: [] for i in range(self.num_parties)
        }

    def get_wire_by_id(self, id: int) -> Wire:
        """
        Returns the wire with the specified ID.

        Args:
            id: The ID of the wire to retrieve.

        Returns:
            Wire: The wire with the specified ID.
        """
        return self._wire_map[id]

    def newSecureInteger(self, wires=None) -> _SecureInt:
        """
        Creates a new _SecureInt object for current circuit.
        If wires are not provided, it will create new wires.

        Args:
            wires: The wires to use for the _SecureInt object.

        Returns:
            _SecureInt: The new _SecureInt object.
        """
        return _SecureInt(self, wires=wires)

    def newWire(self, bit_value: int = None) -> Wire:
        """
        Creates a new wire with the specified bit value.
        If input bit is specified, the wire will be marked as a constant wire.

        Args:
            bit_value (int): The bit value to use for the new wire.

        Returns:
            Wire: The new wire.
        """
        wire = Wire(self, wire_id=len(self.wires), bit_value=bit_value)

        # Add wire to circuit
        self.wires.append(wire)
        self._wire_map[wire.id] = wire

        return wire

    def assign_to_party(self, party_idx: int, name: str, variable: Wire | Wires) -> None:
        """
        Assigns a wire object or wires object to a party.

        Args:
            party_idx (int): The index of the party to assign the wire or wires to.
            name (str): The name of the wire or wires.
            variable (Wire | Wires): The wire or wires to assign to the party.

        Raises:
            Exception: If variable is not Wire or Wires
        """
        if isinstance(variable, Wires) or isinstance(variable, Wire):
            variable.set_as_input_wires(party_idx)

            # Create input object and add to self.inputs
            input_obj = CircuitInput(
                len(self.inputs[party_idx]), name, party_idx, variable
            )
            self.inputs[party_idx].append(input_obj)
        else:
            raise Exception

    def set_output(self, name: str, variable: Wire | Wires) -> None:
        """
        Set given Wire or Wires object as output variable of the program.

        Args:
            name (str): The name of the wire or wires.
            variable (Wire | Wires): The wire or wires to assign to the party.

        Raises:
            Exception: If object is not Wire or Wires
        """
        if not isinstance(variable, Wires) and not isinstance(variable, Wire):
            raise Exception

        variable.set_output()
        self.outputs.append(CircuitOutput(name, variable))

    def _full_subtractor(
        self, wire1: Wire, wire2: Wire, carry_in: Wire
    ) -> Tuple[Wire, Wire]:
        xor_result = wire1 ^ wire2
        out = carry_in ^ xor_result

        and_result = wire1.__not__() & wire2
        carry_and_result = xor_result.__not__() & carry_in
        borrow = carry_and_result | and_result

        return out, borrow

    def _full_adder(self, wire1: Wire, wire2: Wire, carry_in: Wire) -> Tuple[Wire, Wire]:
        """
        Creates a full adder circuit with given input wire and carry wire.

        Args:
            wire1: The first input wire.
            wire2: The second input wire.
            carry_in: The carry-in wire.

        Returns:
            A tuple of two wires: the sum wire and the carry-out wire.
        """
        wires_xor = wire1 ^ wire2
        wires_and = wire1 & wire2

        sum_wire = carry_in ^ wires_xor
        carry_out = (carry_in & wires_xor) | wires_and

        return (sum_wire, carry_out)

    def _and(self, wire1: Wire, wire2: Wire) -> Wire:
        """
        Update circuit by adding an AND gate with wire1 and wire2 as input.

        Args:
            wire1: The first input wire.
            wire2: The second input wire.

        Returns:
            The output wire of the AND gate.
        """
        gate = AndGate(self, wire1, wire2)

        return gate.output_wire

    def _or(self, wire1: Wire, wire2: Wire) -> Wire:
        """
        Update circuit by adding an OR gate with wire1 and wire2 as input.

        Args:
            wire1: The first input wire.
            wire2: The second input wire.

        Returns:
            The output wire of the OR gate.
        """
        gate = OrGate(self, wire1, wire2)

        return gate.output_wire

    def _xor(self, wire1: Wire, wire2: Wire) -> Wire:
        """
        Update circuit by adding an XOR gate with wire1 and wire2 as input.

        Args:
            wire1: The first input wire.
            wire2: The second input wire.

        Returns:
            The output wire of the XOR gate.
        """
        gate = XorGate(self, wire1, wire2)

        return gate.output_wire

    def _xnor(self, wire1: Wire, wire2: Wire) -> Wire:
        """
        Update circuit by adding an XNOR gate with wire1 and wire2 as input.

        Args:
            wire1: The first input wire.
            wire2: The second input wire.

        Returns:
            The output wire of the XNOR gate.
        """
        gate = XnorGate(self, wire1, wire2)

        return gate.output_wire

    def create_garble_cricuit(self) -> Dict[int, List[str]]:
        """
        Create garble circuit.

        Returns:
            garbled circuit: Dictionary where key is gate id, and value is list
                of encrypted truth table rows of the gate.
        """

        return {gate.id: gate.create_grabled_truth_table() for gate in self.gates}

    def get_encrypted_circuit_metadata(self):
        """
        Returns encrypted circuit and its metadata to be sent to circuit evaluater.

        Returns:
            data: Dictionary containing garbled_table, gate_prerequisites, inputs, outputs,
                and const_keys.
        """
        garbled_table = self.create_garble_cricuit()
        gate_prerequisites = self.get_gate_prerequisites()
        inputs = [dict(input_info) for input_info in self.inputs[1]]

        return dict(
            name=self.name,
            garbled_table=garbled_table,
            gate_prerequisites=gate_prerequisites,
            inputs=inputs,
            outputs=list(map(dict, self.outputs)),
            const_keys=self.const_keys,
        )

    def get_gate_prerequisites(self):
        """
        Return graph prerequisites for circuit evaluater to get keys of parent gates.

        Returns:
            prerequisites: List of tuples (parent_wire1, parent_wire2, child_wire)
        """
        output: List[Tuple] = []

        input_wire_ids = set([wire.id for wire in self.wires if wire.is_input_wire])

        for gate in self.gates:
            gate_has_input_wire = False
            for wire in gate.input_wires:
                if wire.id in input_wire_ids:
                    gate_has_input_wire = True
                    break

            # Don't include gates having input wires as they must be evaluated first
            if gate_has_input_wire:
                continue

            output.append((*(wire.id for wire in gate.input_wires), gate.output_wire.id))

        return output
