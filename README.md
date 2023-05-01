# pySecureCircuit

pySecureCircuit is a Python library that allows secure multiparty computation using Yao's garbled circuit technique. The library provides a way for multiple parties to securely compute a function on their private inputs without revealing them to each other, using a combination of encryption, randomization, and computation over circuits.

## Getting Started

### Installation

Run the following command to install the library: 
```sh
pip install pysecurecircuit
```

## Usage

Here's a simple example of how to use pySecureCircuit for the Millionaire's Problem for two parties.

Write your function logic in a python script.

```python
from pysecurecircuit.circuit import Circuit
from pysecurecircuit.server import Server


def main():
    # Create circuit with 2 party
    circuit = Circuit(name="Millionaires' Problem", num_parties=2)

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
    Server(circuit).start()

main()
```

#### Server

To start server for the circuit creator run

```sh
python3 script.py --host 0.0.0.0 --port PORT
```

#### Client

For circuit evaluator, run the following command

```sh
python3 -m pysecurecircuit --client-id CLIENT_ID --host HOST --port PORT
```

Where `CLIENT_ID` is the identifier of the client that starts from 1, `HOST` is the IP address or hostname of the server, and `PORT` is the port number to connect to.

## Contributing

Contributions are welcome! If you'd like to contribute to pySecureCircuit, please fork the repository and create a pull request.

## Acknowledgments

This library is based on Yao's garbled circuit technique, and builds on existing work in secure multiparty computation. Thank you to the researchers and developers who have contributed to this field.
