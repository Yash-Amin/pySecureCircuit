from pysecurecircuit.circuit.gates.gate import Gate


class XorGate(Gate):
    name = "Xor"

    def evaluate(self, input1: int, input2: int) -> int:
        return 1 if input1 != input2 else 0
