""" Game entity management """

from __future__ import annotations
from typing import Union, Type
from app.firebase_utils import db, firestore
from app.user import User, NoUser


class NoGame:
    """ Return value for when no game is found """


class Game:
    @classmethod
    def new(cls, user: User, fork_url: str) -> Game:
        """ Create a new game if doesn't exist, return reference to it """
        from app.quest import Quest  # avoid circular import

        if not user or not fork_url:
            raise ValueError("User or fork can't be blank")

        game = cls()
        game.user = user

        # create game if doesn't exist
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
            db.collection("system").document("stats").update(
                {"games": firestore.Increment(1)}
            )

        # create starting quest if not exist
        QuestClass = Quest.get_first()
        quest = QuestClass.new(game)

        return game

    @classmethod
    def find_by_user(cls, user: User) -> Union[Game, Type[NoGame]]:
        """ Find a game by user_key and return ref object for it, or None """
        docs = db.collection("game").where("user_key", "==", user.key).stream()
        for doc in docs:
            game = cls()
            game.user = user
            return game
        return NoGame

    user: Union[User, Type[NoUser]] = NoUser

    @property
    def key(self) -> str:
        if isinstance(self.user, User):
            return f"{self.user.key}"
        raise AttributeError("user parent not valid")

    def assign_to_uid(self, uid: str) -> None:
        db.collection("game").document(self.key).set({"user_uid": uid}, merge=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(user={repr(self.user)})"
