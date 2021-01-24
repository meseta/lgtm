""" github-related models """
from pydantic import BaseModel, Field, Extra  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
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
