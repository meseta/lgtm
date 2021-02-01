""" Game entity management """

from __future__ import annotations

from orm import Orm
from user import User

from .models import GameData


class Game(Orm, collection="game", parent_orm=User):
    data: GameData
    storage_model = GameData

    @classmethod
    def from_user(cls, user: User) -> Game:
        key = cls.make_key(user)
        game = cls(key)
        game.parent_key = user.key
        return game

    @staticmethod
    def make_key(user: User) -> str:
        """ Game's key ARE user key due to 1:1 relationship """
        return user.key

    def set_fork_url(self, fork_url: str) -> None:
        self.data.fork_url = fork_url
