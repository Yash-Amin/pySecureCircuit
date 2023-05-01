import argparse

from pysecurecircuit.client import Client


def start_client() -> None:
    """Connect to server and evaluate circuit."""
    parser = argparse.ArgumentParser(description="puSecureCircuit Client")

    parser.add_argument("--client-id", type=int, help="Client ID", required=False)
    parser.add_argument("--host", type=str, help="The host to connect to", required=True)
    parser.add_argument("--port", type=int, help="The port to connect to", required=True)

    args = parser.parse_args()

    # TODO: client id is hardcoded as only two parties are supported
    Client(client_id=1, host=args.host, port=args.port).run()


if __name__ == "__main__":
    start_client()
