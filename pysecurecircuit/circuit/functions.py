from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pysecurecircuit.secure_types import Wires, Wire


def if_else(
    condition: Wire, true_return_value: Wires, false_return_value: Wires
) -> Wires:
    """
    Creates 2x1 Multiplexer in the circuit, returns value corresponding to
    the condition wire.

    Returns:
        Wires: Output wires based on condition
    """
    true_wires = true_return_value & condition
    false_wires = false_return_value & condition.__not__()

    return true_wires | false_wires


def secure_max(val1: Wires, val2: Wires):
    """
    Uses if_else to return wires that has maximum value.

    Returns:
        Wires: Output wires based on condition
    """
    return if_else(val1 > val2, val1, val2)
