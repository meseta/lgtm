""" Game entity management """

from __future__ import annotations
from typing import Union, NewType, TYPE_CHECKING

from app.firebase_utils import db, firestore
from app.quest import get_first_quest

if TYPE_CHECKING:
    from app.user import User  # pragma: no cover

NoGameType = NewType("NoGameType", object)
NoGame = NoGameType(object())


class Game:
    def __init__(self, user: User):
        self.user = user

    def new(self, fork_url: str):
        """ Create a new game if doesn't exist """

        if not fork_url:
            raise ValueError("Fork can't be blank")

        game_doc = db.collection("game").document(self.key).get()
        if game_doc.exists:
            game_doc.reference.set(
                {
                    "fork_url": fork_url,
                    "user_uid": self.user.uid,
                    "user_key": self.user.key,
                },
                merge=True,
            )
        else:
            game_doc.reference.set(
                {
                    "fork_url": fork_url,
                    "user_uid": self.user.uid,
                    "user_key": self.user.key,
                    "joined": firestore.SERVER_TIMESTAMP,
                }
            )
            db.collection("system").document("stats").update(
                {"games": firestore.Increment(1)}
            )

        # create starting quest if not exist
        QuestClass = get_first_quest()
        quest = QuestClass(self)
        quest.execute_stages()
        quest.save()

    @property
    def key(self) -> str:
        return f"{self.user.key}"

    def assign_to_uid(self, uid: str) -> None:
        db.collection("game").document(self.key).set({"user_uid": uid}, merge=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(user={repr(self.user)})"


def find_game_by_user(user: User) -> Union[Game, NoGameType]:
    """ Find a game by user_key and return ref object for it, or None """
    docs = db.collection("game").where("user_key", "==", user.key).stream()
    for _ in docs:
        return Game(user)
    return NoGame
