""" Models for validation pubsub payloads """
from typing import Optional
from base64 import b64decode
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
class BaseModelWithPubSub(BaseModel):
    """ Extra decode functions for pubsub data """

    @classmethod
    def from_base64(cls, data: bytes):
        return cls.parse_raw(b64decode(data).decode("utf-8"))


class NewGameData(BaseModelWithPubSub):
    """ Create a new game """

    source: str = Field(..., title="User source, e.g. 'github'")
    userId: str = Field(..., title="User ID")
    userUid: Optional[str] = Field(None, title="Auth UID if known")
    forkUrl: str = Field(..., title="URL of the LGTM fork")
