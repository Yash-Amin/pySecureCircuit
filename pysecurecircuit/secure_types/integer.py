from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

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

    def __init__(self, circuit: Circuit, wires=None, carry_out: Wire = None) -> None:
        super().__init__(circuit=circuit, num_wires=self.num_wires, wires=wires)

        # Carry out wire
        self.carry_out: Wire = carry_out

    def get_value(self) -> int:
        """Returns integer value of bits"""
        output = 0

        for i in range(self.num_wires):
            if self.wires[i].bit_value == 1:
                output += 2 ** (self.bit_length - i - 1)

        return output

    def convert_wires_to_int(self, wires: Wires) -> _SecureInt:
        return _SecureInt(circuit=self.circuit, wires=wires)

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

        return _SecureInt(circuit=self.circuit, wires=output_wires, carry_out=carry_wire)

    def __sub__(self, obj: _SecureInt) -> _SecureInt:
        """
        Uses full subtractor for subtraction of two SecureIntegers.

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
            sum_wire, carry_out_wire = self.circuit._full_subtractor(
                wires1[i], wires2[i], carry_wire
            )
            carry_wire = carry_out_wire
            output_wires[i] = sum_wire

        return _SecureInt(circuit=self.circuit, wires=output_wires, carry_out=carry_wire)

    def __mul__(self, obj: _SecureInt) -> _SecureInt:
        """
        Multiplication of two SecureInt objects

        Retuns:
            _SecureInt: Secure Integer object
        """
        if not isinstance(obj, _SecureInt):
            raise Exception("given object is not SecureInt")

        # TODO: REFACTOR THIS
        # Create list of and_wires corresponding to each bit of obj
        and_wires = list(reversed([self & obj.wires[i] for i in range(self.num_wires)]))

        def shilf_right(left_val: Wire, int_obj: _SecureInt) -> Tuple[_SecureInt, Wire]:
            """
            Shifts intger to right.
            Returns tuple of (New Integer Object, Right-most Wire)
            """
            new_int_wires = [left_val] + int_obj.wires[:-1]

            return (
                _SecureInt(circuit=self.circuit, wires=new_int_wires),
                int_obj.wires[-1],
            )

        output_wires = []

        sum_int, output_wire = shilf_right(self.circuit.newWire(0), and_wires[0])
        output_wires.append(output_wire)

        for i in range(1, self.num_wires):
            new_sum_int = sum_int + and_wires[i]
            new_int, last_wire = shilf_right(new_sum_int.carry_out, new_sum_int)

            sum_int = new_int
            output_wires.insert(0, last_wire)

        return _SecureInt(circuit=self.circuit, wires=output_wires[-self.num_wires :])

    def __truediv__(self, obj: _SecureInt) -> _SecureInt:
        raise NotImplemented

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
