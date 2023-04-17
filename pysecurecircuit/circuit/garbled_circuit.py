from typing import Dict, List

from pysecurecircuit.circuit.gates import GarbledGate


class GarbledCircuit:
    """
    A class representing a garbled circuit.
    """ 

    def __init__(
        self,
        garbled_tables: Dict[int, List[str]],
        outputs: List[Dict],
        constant_wire_keys: Dict[int, str],
    ) -> None:
        """
        Initialize a GarbledCircuit object with the given garbled tables and outputs.

        Args:
            garbled_tables: a dictionary of garbled tables, where the keys are
                the IDs of the gates and the values are lists of strings representing
                the encrypted truth table row
            outputs: a list of dictionaries representing the circuit outputs, where
                each dictionary has 'name', 'kind', and 'wires' keys
            constant_wire_keys: Dictionary contains wire_id to wire's key mapping
        """
        # Create dictionary of gate_id to GarbledGate objects from garbled_tables dict
        self.gates: Dict[int, GarbledGate] = {
            int(key): GarbledGate(int(key), table)
            for key, table in garbled_tables.items()
        }

        # Store the IDs of unevaluated gates in a list
        self.unevaluated_gates = list(sorted(self.gates.keys()))

        # Contains output wire information
        self.outputs: List[Dict] = outputs

        # Keys for constant values
        self.constant_keys: Dict[int, str] = {}
        for key, val in constant_wire_keys.items():
            self.constant_keys[int(key)] = val

    def get_key_of_node(self, node_id: int) -> str:
        """
        Return key of a node(gate or constant wire)

        Args:
            node_id: ID of the node

        Returns:
            key: Key of the node
        """
        if node_id in self.constant_keys:
            return self.constant_keys[node_id]

        if node_id in self.gates:
            return self.garbled_circuit.gates[node_id].output_key.decode()

        raise Exception(f"Key with id {node_id} not found")

    def calculate_output(self):
        """
        Calculates the output of the circuit.
        """
        output_data: List[Dict] = []
        for output_info in self.outputs:
            output_value = None

            variable_name = output_info["name"]
            kind = output_info["kind"]
            wires = output_info["wires"]

            if kind == "wire":
                output_value = int(self.gates[wires[0]].output_key)
            elif kind == "int":
                # Create int from bitstring
                output_value = int(
                    b"".join([self.gates[wire_id].output_key for wire_id in wires]), 2
                )
            else:
                raise NotImplemented
            output_data.append(dict(name=variable_name, kind=kind, value=output_value))

        return output_data

    def __repr__(self) -> str:
        return f"GarbledCircuit({self.gates=})"
