from pysecurecircuit.circuit.gates.gate import Gate


class XnorGate(Gate):
    name = "xnor"

    def evaluate(self, input1: int, input2: int) -> int:
        return 1 if input1 == input2 else 0
