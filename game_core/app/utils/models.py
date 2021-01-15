""" Models for validation pubsub payloads """
from typing import Optional
import base64
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
class BaseModelWithPubSub(BaseModel):
    """ Extra decode functions for pubsub data """

    @classmethod
    def from_base64(cls, data: bytes):
        return cls.parse_raw(base64.b64decode(data).decode("utf-8"))

    @classmethod
    def from_event(cls, event: dict):
        return cls.from_base64(event["data"])


class NewGameData(BaseModelWithPubSub):
    """ Create a new game """

    userId: str = Field(..., title="User ID")
    userUid: Optional[str] = Field(None, title="Auth UID if known")
    forkUrl: str = Field(..., title="URL of the LGTM fork")
