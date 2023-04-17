import time
from typing import List

import zmq
import argparse

from pysecurecircuit.ot import ot_send
from pysecurecircuit import const
from pysecurecircuit.circuit import Circuit
from pysecurecircuit import utils


class Server:
    def __init__(self, circuit: Circuit, host: str = None, port: int = None) -> None:
        self.circuit = circuit
        self.host = host
        self.port = port

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='puSecureCircuit Server')
        
        parser.add_argument('--host', type=str, help='The host to connect to', required=True)
        parser.add_argument('--port', type=int, help='The port to connect to', required=True)
        
        args = parser.parse_args()
        
        return args.host, args.port

    def take_user_inputs(self):
        server_inputs = [dict(input_info) for input_info in self.circuit.inputs[0]]
        if not server_inputs:
            return

        input_wire_values = utils.take_user_input(server_inputs)
        for wire_id, bit_value in input_wire_values.items():
            self.circuit._wire_map[wire_id].set_value(bit_value)


    def start(self):
        if self.host is None or self.port is None:
            self.host, self.port = self.parse_arguments()
        self.take_user_inputs()
        
        print(f"[!] Server started on {self.host}:{self.port}")
        
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(f"tcp://{self.host}:{self.port}")

        while True:
            message = self.socket.recv_json()
            request_type = message["request"]
            data = message["payload"]

            if request_type == const.REQ_FETCH_GARBLED_TABLE:
                print("[!] Initial connection")
                self.socket.send_json(self.circuit.get_encrypted_circuit_metadata())
                print("[!] Garbled circuit was sent to client")
            elif request_type == const.REQ_FETCH_GARBLED_GATE_INPUT_KEYS:
                self.socket.send_json(
                    self.get_garbled_gate_input_keys(data["gate_id"]),
                )
            elif request_type == const.REQ_OT_KEY_TRANSFER:
                self.socket.send_json(
                    # self.ot_key(data["input_bit"], data["wire_id"], data["party_id"]),
                    self.ot_key(data["public_keys"], data["wire_id"], data["party_id"]),
                )
            elif request_type == const.REQ_CONST_VALUE_KEY_TRANSFER:
                self.socket.send_json(self.circuit.const_keys)
            elif request_type == const.REQ_CLOSE_CONNECTION:
                self.socket.send(b"")
                self.socket.close()
            elif request_type == const.REQ_OUTPUT:
                utils.print_output(data)
                self.socket.send(b"")
                self.socket.close()
                break

    def get_garbled_gate_input_keys(self, gate_id: int):
        gate = self.circuit._gate_map[gate_id]

        input_wires = gate.input_wires
        keys_info = []

        for wire in input_wires:
            if wire.party_id == -1:
                # internal wire
                # keys_info.append(None)
                keys_info.append(dict(wire_id=wire.id, key=None))
            elif wire.party_id == 0:
                # TODO: set value
                val = wire.keys[wire.bit_value]
                keys_info.append(dict(wire_id=wire.id, key=val))
            elif wire.party_id == 1:
                keys_info.append(dict(wire_id=wire.id, party_id=wire.party_id))
            elif wire.party_id > 1:
                raise NotImplemented

        return dict(gate_id=gate_id, keys_info=keys_info)

    # def ot_key(self, input_bit: int, wire_id: int, party_id: int):
    def ot_key(self, public_keys: List[str], wire_id: int, party_id: int):
        if party_id != 1:
            raise NotImplemented

        wire = self.circuit.get_wire_by_id(wire_id)
        if wire.party_id != party_id:
            return {"msg": "error"}

        return dict(encrypted_values=ot_send(wire.keys, public_keys))

        # return {"key": wire.keys[input_bit]}
