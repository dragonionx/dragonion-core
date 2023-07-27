from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Final

from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

from ...encryption.identity import Identity


@dataclass_json
@dataclass
class WebMessageMessage:
    """
    Sent as regular message
    :param username: From user
    :param message: Encrypted b64-encoded message
    """
    username: str
    avatar: str
    message: bytes
    type: Final = "message"
    time: datetime = None

    def decrypt(self, identity: Identity):
        return identity.decrypt(self.message)


@dataclass_json
@dataclass
class WebBroadcastableMessage:
    """
    Out-coming message, generated by WebBroadcastableBuilder
    :param messages: Dict
    """

    messages: dict[str, WebMessageMessage] = field(default_factory=dict)
    type: Final = "broadcastable"
    time: datetime = None


@dataclass
class WebBroadcastableBuilder:
    """
    Class for creating outcoming messages
    :param from_user: User, that send message
    :param message_content: Text of message
    :param keys: Dict with public keys in format username:public_key
    """
    from_user: str
    avatar: str
    message_content: str
    keys: dict[str, bytes]

    broadcastable: WebBroadcastableMessage = field(
        default_factory=WebBroadcastableMessage
    )

    def __post_init__(self):
        for username in self.keys.keys():
            public_key = serialization.load_der_public_key(
                base64.urlsafe_b64decode(self.keys[username])
            )

            self.broadcastable.messages[username] = WebMessageMessage(
                username=self.from_user,
                avatar=self.avatar,
                message=base64.urlsafe_b64encode(public_key.encrypt(
                    self.message_content.encode(),
                    padding=padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ))
            )

    def to_json(self):
        """
        Convert to json
        :return: Only encrypted data, that can be sent to server
        """
        return self.broadcastable.to_json()
