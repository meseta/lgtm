""" Game entity management """

from __future__ import annotations
from typing import Union, NewType, TYPE_CHECKING

from app.firebase_utils import db, firestore
from app.quest import Quest
from app.user import NoUser
from app.tick import TickType

if TYPE_CHECKING:
    from app.user import User, NoUserType  # pragma: no cover

NoGameType = NewType("NoGameType", object)
NoGame = NoGameType(object())


class Game:
    @classmethod
    def from_user(cls, user: User) -> Union[Game, NoGameType]:
        """ Create a game from a user """
        key = cls.make_key(user)
        game = cls(key)
        game.user = user

        docs = db.collection("game").where("user_key", "==", user.key).stream()
        for _ in docs:
            return game
        return NoGame

    @classmethod
    def new_from_fork(cls, user: User, fork_url: str) -> Game:
        """ Save game with fork """

        if not fork_url:
            raise ValueError("Fork can't be blank")

        key = cls.make_key(user)
        game = cls(key)
        game.user = user

        game_doc = db.collection("game").document(game.key).get()
        if game_doc.exists:
            game_doc.reference.set(
                {
                    "fork_url": fork_url,
                    "user_uid": user.uid,
                    "user_key": user.key,
                },
                merge=True,
            )

        else:
            game_doc.reference.set(
                {
                    "fork_url": fork_url,
                    "user_uid": user.uid,
                    "user_key": user.key,
                    "joined": firestore.SERVER_TIMESTAMP,
                }
            )
            # db.collection("system").document("stats").update(
            #     {"games": firestore.Increment(1)}
            # )

        return game

    @staticmethod
    def make_key(user: User) -> str:
        """ Game's key ARE user key due to 1:1 relationship """
        return user.key

    key: str
    user: Union[User, NoUserType]

    def __init__(self, key: str):
        self.key = key
        self.user = NoUser

    def assign_to_uid(self, uid: str) -> None:
        """ Assign a user to this game """
        doc = db.collection("game").document(self.key).get()
        if doc.exists:
            doc.reference.set({"user_uid": uid}, merge=True)

    def start_first_quest(self) -> None:
        """ Create starting quest if not exist """
        QuestClass = Quest.get_first_quest()
        quest = QuestClass.from_game(self)
        quest.execute_stages(TickType.FULL)
        quest.save()

    def __repr__(self):
        return f"{self.__class__.__name__}(key={self.key})"
