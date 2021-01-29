""" User entity management, note: User entities in firestore are not necessary auth users """

from __future__ import annotations
from typing import Union, NewType, TYPE_CHECKING
from enum import Enum

from app.firebase_utils import db, firestore

if TYPE_CHECKING:
    from app.models import UserData  # pragma: no cover

NoUserType = NewType("NoUserType", object)
NoUser = NoUserType(object())


class Source(Enum):
    """ Source and user_id form a tuple to identify users """

    TEST = "test"
    GITHUB = "github"


class User:
    """A user object, potentially referencing an object in the database.
    Unusaully, users in the database will only exist if they have an uid
    But games can reference users not-yet in the database by their
    source/user_id, so it is possible to reference hypothetical users
    This user object represents a hypothetical user"""

    def __init__(self, source: Source, user_id: str):
        if not source or not user_id:
            raise ValueError("source or user_id can't be blank")
        self.source = source
        self.user_id = user_id
        self.uid = ""

    def create_with_data(self, uid: str, user_data: UserData) -> None:
        """ Creates new user from user_data """
        self.uid = uid
        doc = db.collection("users").document(uid).get()
        if not doc.exists:
            doc.reference.set(
                {
                    **user_data.dict(),
                    "joined": firestore.SERVER_TIMESTAMP,
                    "source": self.source.value,
                    "user_key": self.key,
                }
            )

            db.collection("system").document("stats").update(
                {"players": firestore.Increment(1)}
            )

    @property
    def key(self) -> str:
        """ Key used as part of database IDs """
        return f"{self.source.value}:{self.user_id}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key})"


def find_user_by_source_id(source: Source, user_id: str) -> Union[User, NoUserType]:
    """ Find a user based on the source+id """
    user = User(source, user_id)
    docs = db.collection("users").where("user_key", "==", user.key).stream()
    for doc in docs:
        user.uid = doc.id
        return user
    return NoUser
