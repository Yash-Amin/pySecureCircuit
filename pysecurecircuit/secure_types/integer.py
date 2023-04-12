from __future__ import annotations

from typing import TYPE_CHECKING

from pysecurecircuit.secure_types import Wire, Wires

if TYPE_CHECKING:
    from pysecurecircuit.circuit import Circuit


class _SecureInt(Wires):
    """
    Secure integer class.
    """

    kind = "int"

    # TODO: update it to 32
    num_wires = 8

    def __init__(self, circuit: Circuit, wires=None) -> None:
        super().__init__(circuit=circuit, num_wires=self.num_wires, wires=wires)

    def get_value(self) -> int:
        """Returns integer value of bits"""
        output = 0

        for i in range(self.num_wires):
            if self.wires[i].bit_value == 1:
                output += 2 ** (self.bit_length - i - 1)

        return output

    def __add__(self, obj: _SecureInt) -> _SecureInt:
        """
        Uses full adder for addition of two SecureIntegers.

        Retuns:
            _SecureInt: Secure Integer object
        """
        if not isinstance(obj, _SecureInt):
            raise Exception("given object is not SecureInt")

        wires1 = self.wires
        wires2 = obj.wires

        carry_wire = self.circuit.newWire(bit_value=0)
        output_wires = [None for _ in range(len(wires1))]

        for i in range(len(wires1) - 1, -1, -1):
            sum_wire, carry_out_wire = self.circuit._full_adder(
                wires1[i], wires2[i], carry_wire
            )
            carry_wire = carry_out_wire
            output_wires[i] = sum_wire

        return _SecureInt(circuit=self.circuit, wires=output_wires)

    def __gt__(self, obj: _SecureInt) -> Wire:
        """
        Returns a wire representing whether self is greater than obj.

        Args:
            obj: A SecureInt object to compare to self.

        Returns:
            A Wire object representing whether self > obj.
        """
        if not isinstance(obj, _SecureInt):
            raise Exception("given object is not SecureInt")

        wires1 = self.wires
        wires2 = obj.wires

        # Compare the most significant bits of self and obj.
        output_wire = wires1[0] > wires2[0]
        msb_xnor_wire = wires1[0].__xnor__(wires2[0])

        # Iterate over remaining bits, from msb to lsb
        for i in range(1, len(wires1)):
            # Calculate the result of the current bit comparison.
            bit_gt = self.wires[i] > obj.wires[i]
            # Calculate the result of the current bit XNOR.
            bit_xnor = self.wires[i].__xnor__(obj.wires[i])
            # Calculate the output wire for the current bit.
            output_wire = output_wire | (msb_xnor_wire & bit_gt)
            # Calculate the XNOR for the next iteration.
            msb_xnor_wire = msb_xnor_wire & bit_xnor

        return output_wire

    def __lt__(self, obj: _SecureInt) -> Wire:
        """
        Returns a wire representing whether self is less than obj.

        Args:
            obj: A SecureInt object to compare to self.

        Returns:
            A Wire object representing whether self < obj.
        """
        # Return the result of obj > self.
        return obj > self

    def __ge__(self, obj: _SecureInt) -> Wire:
        """
        Returns a wire representing whether self is greater than or equal to obj.

        Args:
            obj: A SecureInt object to compare to self.

        Returns:
            A Wire object representing whether self >= obj.
        """
        # Return the negation of self < obj.
        return (self < obj).__not__()

    def __le__(self, obj: _SecureInt) -> Wire:
        """
        Returns a wire representing whether self is less than or equal to obj.

        Args:
            obj: A SecureInt object to compare to self.

        Returns:
            A Wire object representing whether self <= obj.
        """
        # Return the result of obj >= self.
        return obj >= self

    def __or__(self, __value: Wire | Wires) -> Wires:
        """
        Perform bitwise OR on __value.

        Args:
            __value: Wire or Wires object

        Returns:
            _SecureInt: Secure integer object
        """
        output_wires = super().__or__(__value)
        return _SecureInt(self.circuit, wires=output_wires.wires)

    def __and__(self, __value: Wire | Wires) -> Wires:
        output_wires = super().__and__(__value)

        return _SecureInt(self.circuit, wires=output_wires.wires)
