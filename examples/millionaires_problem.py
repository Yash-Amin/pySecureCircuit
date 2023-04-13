"""
Millionaires' Problem: Two parties are interested in knowing who is richer without revealing their wealth.

The below example creates a circuit for 2 users: Alice and Bob.
Alice creates a program that creates a circuit for 2 inputs which calculates alice_wealth > bob_wealth.

To run for alice, run "python3 millionairs_problem.py", this will start server on 5000 port.
To run for bob, run "python3 -m pysecurecircuit.client -P 1 --host '127.0.0.1' --port 5000"
When Bob connects to the server, both users will be required to input their wealth, and then
pySecureCircuit
"""
from pysecurecircuit.circuit import Circuit
from pysecurecircuit.server import Server


def main():
    # Create circuit with 2 party
    circuit = Circuit(num_parties=2)

    # Define input variable
    alice_wealth = circuit.newSecureInteger()
    bob_wealth = circuit.newSecureInteger()

    # Circuit logic
    alice_richer_than_bob = alice_wealth > bob_wealth

    # Assign input variables to alice and bob
    circuit.assign_to_party(party_idx=0, name="Wealth (Alice)", variable=alice_wealth)
    circuit.assign_to_party(party_idx=1, name="Wealth (Bob)", variable=bob_wealth)

    # Set circuit's output
    circuit.set_output(name="Alice richer than Bob", variable=alice_richer_than_bob)

    # Start server
    Server(circuit, "0.0.0.0", 5000).start()


main()
