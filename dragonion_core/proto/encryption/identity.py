from attrs import define
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64


@define
class Identity:
    """
    Valid identity has fields
    username - in most cases same as filename, represents identity's username
    private_key - key to decrypt incoming messages and get public key,
                  shouldn't be sent anywhere, generated via generate function
    """
    username: str
    private_key: rsa.RSAPrivateKey = None

    def generate(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )

    def public_key(self):
        return base64.urlsafe_b64encode(self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.PKCS1
        ))
