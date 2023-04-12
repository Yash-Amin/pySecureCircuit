import time

import zmq

from pysecurecircuit import const
from pysecurecircuit.circuit import Circuit


class Server:
    def __init__(self, circuit: Circuit, host: str, port: int) -> None:
        self.circuit = circuit
        self.host = host
        self.port = port

    def start(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(f"tcp://{self.host}:{self.port}")

        while True:
            message = self.socket.recv_json()
            request_type = message["request"]
            data = message["payload"]

            print(f"Received request: {message}")

            if request_type == const.REQ_FETCH_GARBLED_TABLE:
                self.socket.send_json(self.circuit.get_encrypted_circuit_metadata())
            elif request_type == const.REQ_FETCH_GARBLED_GATE_INPUT_KEYS:
                self.socket.send_json(
                    self.get_garbled_gate_input_keys(data["gate_id"]),
                )
            elif request_type == const.REQ_OT_KEY_TRANSFER:
                self.socket.send_json(
                    self.ot_key(data["input_bit"], data["wire_id"], data["party_id"]),
                )
            elif request_type == const.REQ_CONST_VALUE_KEY_TRANSFER:
                self.socket.send_json(self.circuit.const_keys)
            elif request_type == const.REQ_CLOSE_CONNECTION:
                self.socket.send(b"")
                self.socket.close()
            # time.sleep(0.2)

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

    def ot_key(self, input_bit: int, wire_id: int, party_id: int):
        if party_id != 1:
            raise NotImplemented

        wire = self.circuit.get_wire_by_id(wire_id)
        if wire.party_id != party_id:
            return {"msg": "error"}

        return {"key": wire.keys[input_bit]}
