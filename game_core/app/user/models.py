""" Models for User data """
from enum import Enum
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Source(Enum):
    """ Source and user_id form a tuple to identify users """

    TEST = "test"
    GITHUB = "github"


class UserData(BaseModel):
    """ Incoming auth data from /web/src/store/auth/types.ts """

    profileImage: str = Field("", title="Profile pic URL")
    name: str = Field("", title="Real name")
    handle: str = Field("", title="Username")
    id: str = Field("", title="User's GitHub ID")
    accessToken: str = Field("", title="GitHub access token")
