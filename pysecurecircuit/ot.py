import rsa

from typing import List, Tuple


def ot_request(value: int) -> Tuple[rsa.PrivateKey, List[str]]:
    # TODO: Fix this
    key_size = 512

    (public_key, private_key) = rsa.newkeys(key_size)
    (fake_public_key, _) = rsa.newkeys(key_size)

    public_key_pem = public_key.save_pkcs1().decode()
    fake_public_key_pem = fake_public_key.save_pkcs1().decode()

    return private_key, (
        [public_key_pem, fake_public_key_pem]
        if value == 0
        else [fake_public_key_pem, public_key_pem]
    )


def ot_send(values: List[str], public_keys: List[str]) -> List[str]:
    encrypted_output = []

    for value, key_pkcs in zip(values, public_keys):
        public_key = rsa.PublicKey.load_pkcs1(key_pkcs)
        encoded_msg = value.encode()

        encrypted_output.append(rsa.encrypt(encoded_msg, public_key).hex())

    return encrypted_output


def ot_decrypt(
    bit_value: int,
    encrypted_values: List[str],
    private_key: rsa.PrivateKey,
) -> str:
    return rsa.decrypt(bytes.fromhex(encrypted_values[bit_value]), private_key).decode()
