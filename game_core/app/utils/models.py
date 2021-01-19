""" Models for validation pubsub payloads """
from typing import Optional
from base64 import b64decode
from pydantic import BaseModel, Field, Extra  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
class BaseModelWithPubSub(BaseModel):
    """ Extra decode functions for pubsub data """

    @classmethod
    def from_base64(cls, data: bytes):
        return cls.parse_raw(b64decode(data).decode("utf-8"))

    @classmethod
    def from_event(cls, event: dict):
        return cls.from_base64(event["data"])


class NewGameData(BaseModelWithPubSub):
    """ Payload between endpoints for creating a new game """

    source: str = Field(..., title="User source, e.g. 'github'")
    userId: str = Field(..., title="User ID")
    forkUrl: str = Field(..., title="URL of the LGTM fork")


class UserData(BaseModel):
    """ Incoming auth data from /web/src/store/auth/types.ts """

    profileImage: str = Field(..., title="Profile pic URL")
    name: str = Field(..., title="Real name")
    handle: str = Field(..., title="Username")
    id: str = Field(..., title="User's GitHub ID")
    accessToken: str = Field(..., title="GitHub access token")


class GitHubUser(BaseModel):
    """ User entity for GitHub hooks """

    login: str = Field(..., title="User's user login name")
    id: int = Field(..., title="User's ID")

    class Config:
        extra = Extra.ignore


class GitHubRepository(BaseModel):
    """ Repository entity for GitHub hooks """

    id: int = Field(..., title="Repo's ID")
    full_name: str = Field(..., title="Repo's full name (including owner)")
    owner: GitHubUser = Field(..., title="Owner of repo")
    url: str = Field(..., title="API RUL of the repo")

    class Config:
        extra = Extra.ignore


class GitHubHookFork(BaseModel):
    """ Webhook payload for GitHub fork hooks """

    forkee: GitHubRepository = Field(..., title="The fork created")
    repository: GitHubRepository = Field(..., title="The repository being forked")

    class Config:
        extra = Extra.ignore
