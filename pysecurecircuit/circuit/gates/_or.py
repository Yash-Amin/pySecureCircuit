from pysecurecircuit.circuit.gates.gate import Gate


class OrGate(Gate):
    name = "Or"

    def evaluate(self, input1: int, input2: int) -> int:
        return 1 if input1 == 1 or input2 == 1 else 0
