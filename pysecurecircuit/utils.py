from typing import List, Dict

from pysecurecircuit.secure_types import _SecureInt


def print_output(outputs: List[Dict]):
    print()
    print("-" * 50)
    print("[!] Evaluated circuit output:")
    print("-" * 50)

    for output in outputs:
        variable_name = output["name"]
        value = output["value"]
        kind = output["kind"]

        print(f"[+] {variable_name} = {value}")
    print("-" * 50)


def _take_int_input(input_info, wire_inputs) -> None:
    value = int(input(f"[+] Enter value for '{input_info['name']}': "))
    if value < 0:
        raise NotImplemented

    bit_str = bin(value)[2:]

    if len(bit_str) > _SecureInt.num_wires:
        raise Exception("Integer overflow")
    elif len(bit_str) < _SecureInt.num_wires:
        bit_str = "0" * (_SecureInt.num_wires - len(bit_str)) + bit_str

    wire_inputs.update(dict(zip(input_info["wires"], map(int, bit_str))))


def take_user_input(inputs: List[Dict]):
    print("[!] Enter input values:")

    wire_inputs: Dict[int, int] = {}

    for input_info in inputs:
        kind = input_info["kind"]

        if kind == _SecureInt.kind:
            _take_int_input(input_info, wire_inputs)
        elif kind == "wire":
            # self.wire_inputs[input_info["wires"][1]] = int(const.BOB_INPUT)
            raise NotImplemented
        else:
            raise NotImplemented

    print("-" * 50)
    print()    

    return wire_inputs
