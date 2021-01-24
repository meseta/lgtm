""" Models for validation pubsub payloads """
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
class UserData(BaseModel):
    """ Incoming auth data from /web/src/store/auth/types.ts """

    profileImage: str = Field(..., title="Profile pic URL")
    name: str = Field(..., title="Real name")
    handle: str = Field(..., title="Username")
    id: str = Field(..., title="User's GitHub ID")
    accessToken: str = Field(..., title="GitHub access token")
