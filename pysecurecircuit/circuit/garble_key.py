class GarbledKey:
    """
    Class representing a key used in a garbled circuit.
    """

    def __init__(
        self,
        key: str = None,
        party_id: int = None,
        wire_id: int = None,
    ) -> None:
        """
        Initialize a GarbledKey object with the given key, party ID and wire ID.

        Args:
            key: the key used in the garbled circuit
            party_id: the ID of the party associated with this key
            wire_id: the ID of the wire associated with this key
        """
        self.key: str = key
        self.party_id = party_id
        self.wire_id = wire_id
