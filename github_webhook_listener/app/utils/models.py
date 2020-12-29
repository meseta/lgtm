""" Models for validation of Github hooks """
from pydantic import BaseModel, Field, Extra  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods,missing-class-docstring
class GitHubUser(BaseModel):
    login: str = Field(..., title="User's user login name")
    id: int = Field(..., title="User's ID")

    class Config:
        extra = Extra.ignore


class GitHubRepository(BaseModel):
    id: int = Field(..., title="Repo's ID")
    full_name: str = Field(..., title="Repo's full name (including owner)")
    owner: GitHubUser = Field(..., title="Owner of repo")
    url: str = Field(..., title="API RUL of the repo")

    class Config:
        extra = Extra.ignore


class GitHubHookFork(BaseModel):
    forkee: GitHubRepository = Field(..., title="The fork created")
    repository: GitHubRepository = Field(..., title="The repository being forked")

    class Config:
        extra = Extra.ignore
