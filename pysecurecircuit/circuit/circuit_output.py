from pysecurecircuit.secure_types import Wire, Wires


class CircuitOutput:
    """
    Class representing an output from a garbled circuit.
    """

    def __init__(self, name: str, variable: Wire | Wires) -> None:
        """
        Initialize a CircuitOutput object with the given name and variable.

        Args:
            name: the name of the output
            variable: the variable that will be evaluated
        """
        self.name = name
        self.variable = variable

    def __iter__(self):
        wires = (
            [self.variable] if isinstance(self.variable, Wire) else self.variable.wires
        )

        d = dict(
            name=self.name, wires=[wire.id for wire in wires], kind=self.variable.kind
        )

        for key, val in d.items():
            yield key, val
