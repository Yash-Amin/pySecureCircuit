from pysecurecircuit.circuit.gates.gate import Gate


class AndGate(Gate):
    name = "And"

    def evaluate(self, input1: int, input2: int) -> int:
        return 1 if input1 == input2 == 1 else 0
