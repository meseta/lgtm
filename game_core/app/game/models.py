""" Models for User data """
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class GameData(BaseModel):
    """ Data to store for game """

    fork_url: str = Field("", title="Url of player's fork")
