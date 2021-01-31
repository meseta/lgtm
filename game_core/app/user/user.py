""" User entity management, note: User entities in firestore are not necessary auth users """

from __future__ import annotations
from typing import Union, NewType, TYPE_CHECKING
from enum import Enum

from firebase_utils import db, firestore

if TYPE_CHECKING:
    from models import UserData  # pragma: no cover

NoUserType = NewType("NoUserType", object)
NoUser = NoUserType(object())


class Source(Enum):
    """ Source and user_id form a tuple to identify users """

    TEST = "test"
    GITHUB = "github"


class User:
    """User class is a hypothetical user, who may or may not be in the database
    The object has a "uid" if it comes from the database
    """

    @classmethod
    def from_source_id(cls, source: Source, user_id: str) -> User:
        """ Create a user from the source+id """
        key = cls.make_key(source, user_id)
        user = cls(key)

        # fetch uid if it exists
        docs = db.collection("users").where("user_key", "==", user.key).stream()
        for doc in docs:
            user.uid = doc.id
            break

        return user

    @classmethod
    def new_from_data(cls, uid: str, source: Source, user_data: UserData) -> User:
        """ Save user to database """

        user = cls.from_source_id(source, user_data.id)
        user.uid = uid

        doc = db.collection("users").document(uid).get()
        if not doc.exists:
            doc.reference.set(
                {
                    **user_data.dict(),
                    "joined": firestore.SERVER_TIMESTAMP,
                    "source": source.value,
                    "user_key": user.key,
                }
            )

            # db.collection("system").document("stats").update(
            #     {"players": firestore.Increment(1)}
            # )
        else:
            doc.reference.set(
                {
                    **user_data.dict(),
                    "source": source.value,
                    "user_key": user.key,
                },
                merge=True,
            )

        return user

    @staticmethod
    def make_key(source: Source, user_id: str) -> str:
        """ Key used as part of database IDs """
        return f"{source.value}:{user_id}"

    @staticmethod
    def key_to_user_id(key: str) -> str:
        return key.split(":")[-1]

    key: str
    uid: str

    def __init__(self, key: str):
        self.key = key
        self.uid = ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.key})"
