""" Game entity management """

from __future__ import annotations
from app.firebase_utils import db
from app.user import User

class Game:
    @classmethod
    def new(cls, user: User, fork_url: str) -> Game:
        """ Create a new game if doesn't exist, return reference to it """
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
                },
                merge=True,
            )
        else:
            game_doc.reference.set(
                {
                    "fork_url": fork_url,
                    "user_uid": user.uid,
                    "joined": firestore.SERVER_TIMESTAMP,
                }
            )

        # create starting quest if not exist
        QuestClass = Quest.get_first()
        quest = QuestClass.new(game)

        return game

    @classmethod
    def find_by_user(cls, user: User) -> Optional[Game]:
        """ Find a game by user_key and return ref object for it, or None """
        docs = (
            db.collection("games")
            .where("user_key", "==", user.user_key)
            .stream()
        )
        for doc in docs:
            return cls(doc.id)
        return None

    user: Optional[User] = None

    @property
    def key(self) -> str:
        if not self.user:
            raise ValueError("user parent not set")
        return f"{self.user.key}"

    def assign_to_uid(self, uid: str) -> None:
        db.collection("games").document(self.game_id).set({"uid": uid}, merge=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(user={repr(self.user)}, fork_url={self.fork_url})"
