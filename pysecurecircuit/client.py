import argparse
from typing import Dict, List

import zmq

from pysecurecircuit import const, utils
from pysecurecircuit.circuit import GarbledCircuit, GarbledGate, GarbledKey
from pysecurecircuit.ot import ot_decrypt, ot_request
from pysecurecircuit.secure_types import _SecureInt


class Client:
    def __init__(
        self,
        client_id: int,
        host: str,
        port: int,
    ) -> None:
        """
        Initializes client object.

        Args:
            client_id: ID of the client
            host: Host
            port: Port
        """
        if client_id <= 0:
            raise Exception("Invalid ID")
        elif client_id > 1:
            # Currently supports two
            raise NotImplemented

        self.client_id = client_id
        self.host = host
        self.port = port

        # Dictionary containing mapping of wire_id to its bit value
        self.wire_inputs: Dict[int, int] = {}

    def send(self, request_type: str, payload: Dict) -> None:
        """
        Send request and payload to server.

        Args:
            request_type: Request type
            payload: Dictionary of data
        """
        self.socket.send_json(dict(request=request_type, payload=payload))

    def run(self):
        """
        Connect to server and evaluate circuit.
        """
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{self.host}:{self.port}")
        print("[!] Client started")

        # Fetch garbled circuit and circuit's metadata
        self.fetch_garbled_circuit()

        # Evaluate circuit
        for gate in self.garbled_circuit.gates.values():
            self.evaluate_gate(gate)

        # Calculate and send circuit's output
        circuit_output = self.garbled_circuit.calculate_output()
        self.send(const.REQ_OUTPUT, circuit_output)
        self.socket.recv()

        utils.print_output(circuit_output)

    def fetch_garbled_circuit(self):
        """
        Fetch garbled circuit from server.
        """
        self.send(const.REQ_FETCH_GARBLED_TABLE, {})
        data = self.socket.recv_json()

        print(f"[!] Received garbled circuit '{data['name']}'")
        # Take input from user
        self.wire_inputs = utils.take_user_input(data["inputs"])

        # Create garbled circuit object
        self.garbled_circuit = GarbledCircuit(
            data["garbled_table"], data["outputs"], data["const_keys"]
        )

        # Create graph of gates and their prerequisites
        gate_edges: List[List[int]] = data["gate_prerequisites"]

        self.circuit_graph: Dict[int, List[int]] = {}

        for edge in gate_edges:
            parent = edge[-1]
            nodes = edge[:-1]

            self.circuit_graph[parent] = nodes

    def evaluate_gate(self, gate: GarbledGate):
        """
        Evaluates garbled gate
        """

        def get_key(node) -> str:
            if node in self.garbled_circuit.gates:
                return self.garbled_circuit.gates[node].output_key.decode()
            return self.garbled_circuit.constant_keys[node]

        # If gate has no prerequisites, then fetch keys using oblivious transfer
        if gate.id not in self.circuit_graph:
            self.fetch_gate_keys(gate)
        else:
            # If gate has prerequisites, then its parent gates are already
            # evaluated and take keys from parent gates
            key0, key1 = [get_key(node) for node in self.circuit_graph[gate.id]]

            gate.input_keys.append(GarbledKey(key=key0))
            gate.input_keys.append(GarbledKey(key=key1))

        gate.evaluate()

    def fetch_key_ot(self, key: GarbledKey):
        wire_value = self.wire_inputs[key.wire_id]

        private_key, public_keys = ot_request(wire_value)

        self.send(
            const.REQ_OT_KEY_TRANSFER,
            dict(
                # input_bit=self.wire_inputs[key.wire_id],
                public_keys=public_keys,
                wire_id=key.wire_id,
                party_id=key.party_id,
            ),
        )

        data = self.socket.recv_json()

        encrypted_values = data["encrypted_values"]

        key.key = ot_decrypt(wire_value, encrypted_values, private_key)
        # key.key = data["key"]

    def fetch_gate_keys(self, gate: GarbledGate):
        self.send(const.REQ_FETCH_GARBLED_GATE_INPUT_KEYS, dict(gate_id=gate.id))
        data = self.socket.recv_json()

        keys_info: List[Dict] = data["keys_info"]

        for key_info in keys_info:
            wire_id = key_info.get("wire_id")
            key = key_info.get("key")

            if not key and wire_id in self.garbled_circuit.gates:
                key = self.garbled_circuit.gates[wire_id].output_key.decode()
            elif not key and wire_id and wire_id in self.garbled_circuit.constant_keys:
                key = self.garbled_circuit.constant_keys[wire_id]

            key = GarbledKey(
                key=key,
                wire_id=wire_id,
                party_id=key_info.get("party_id"),
            )

            gate.input_keys.append(key)
            if key.key is None:
                self.fetch_key_ot(key)

    def _take_int_input(self, input_info) -> None:
        # value = const.BOB_INPUT
        value = int(input(f"[+] Enter value for '{input_info['name']}': "))
        if value < 0:
            raise NotImplemented

        bit_str = bin(value)[2:]

        if len(bit_str) > _SecureInt.num_wires:
            raise Exception("Integer overflow")
        elif len(bit_str) < _SecureInt.num_wires:
            bit_str = "0" * (_SecureInt.num_wires - len(bit_str)) + bit_str

        self.wire_inputs.update(dict(zip(input_info["wires"], map(int, bit_str))))

    def take_user_input(self, inputs: List[Dict]):
        for input_info in inputs:
            kind = input_info["kind"]

            if kind == _SecureInt.kind:
                self._take_int_input(input_info)
            elif kind == "wire":
                self.wire_inputs[input_info["wires"][1]] = int(const.BOB_INPUT)
            else:
                raise NotImplemented
