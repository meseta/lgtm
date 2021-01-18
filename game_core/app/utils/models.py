""" Models for validation pubsub payloads """
from typing import Optional
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
class NewGameData(BaseModel):
    """ Create a new game """

    source: str = Field(..., title="User source, e.g. 'github'")
    userId: str = Field(..., title="User ID")
    userUid: Optional[str] = Field(None, title="Auth UID if known")
    forkUrl: str = Field(..., title="URL of the LGTM fork")
