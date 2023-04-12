from pysecurecircuit.secure_types import Wire, Wires


class CircuitInput:
    """
    Class representing an input of the circuit.
    """

    def __init__(
        self, id: int, name: str, party_idx: int, variable: Wire | Wires
    ) -> None:
        """
        Initialize a CircuitInput object with the given id, name, party index, and variable.

        Args:
            id: the ID of the input
            name: the name of the input
            party_idx: the index of the party providing the input
            variable: the variable that requires input
        """
        self.id = id
        self.name = name
        self.party_idx = party_idx
        self.variable = variable
        self.kind = self.variable.kind

    def __iter__(self):
        wires = (
            [self.variable] if isinstance(self.variable, Wire) else self.variable.wires
        )

        d = dict(
            id=self.id,
            name=self.name,
            wires=[wire.id for wire in wires],
            kind=self.variable.kind,
        )

        for key, val in d.items():
            yield key, val
