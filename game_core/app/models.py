""" Models for validation pubsub payloads """
from typing import Optional
from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    Field,
    root_validator,
)

# pylint: disable=too-few-public-methods,missing-class-docstring
class UserData(BaseModel):
    """ Incoming auth data from /web/src/store/auth/types.ts """

    profileImage: str = Field(..., title="Profile pic URL")
    name: str = Field(..., title="Real name")
    handle: str = Field(..., title="Username")
    id: str = Field(..., title="User's GitHub ID")
    accessToken: str = Field(..., title="GitHub access token")


class StatusReturn(BaseModel):
    """ Generic ok status """

    success: bool = Field(False, title="Whether action was ok")
    error: Optional[str] = Field(None, title="Errors if any")
    http_code: Optional[int] = Field(None, title="HTTP response code")

    @root_validator
    def set_http_code(cls, values):
        if values["http_code"] is not None:
            return values

        if values["success"]:
            values["http_code"] = 200
        else:
            values["http_code"] = 400

        return values


class TickEvent(BaseModel):
    """ Model for ticks """

    source: str = Field(..., title="Source of the tick")
