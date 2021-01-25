""" User entity management, note: User entities in firestore are not necessary auth users """

from __future__ import annotations
from typing import Union, NewType
from enum import Enum

from app.models import UserData
from app.firebase_utils import db, firestore

NoUserType = NewType("NoUserType", object)
NoUser = NoUserType(object())


class Source(Enum):
    """ Source and user_id form a tuple to identify users """

    TEST = "test"
    GITHUB = "github"


class User:
    """ A user entity. Users can either be identified by source+id or uid """

    @classmethod
    def reference(cls, source: Source, user_id: str) -> User:
        """ Creates a user reference - note this doesn't check if the user exists """
        return cls(source=source, user_id=user_id)

    @classmethod
    def new(cls, uid: str, source: Source, user_data: UserData) -> User:
        """ Create a new user, providing the full uid, source, and user_data model """
        user = cls(source=source, user_id=user_data.id)
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

            db.collection("system").document("stats").update(
                {"players": firestore.Increment(1)}
            )
        user.uid = uid
        return user

    @classmethod
    def find_by_source_id(cls, source: Source, user_id: str) -> Union[User, NoUserType]:
        """ Find a user based on the source+id """
        user = cls(source, user_id)
        docs = db.collection("users").where("user_key", "==", user.key).stream()
        for doc in docs:
            user.uid = doc.id
            return user
        return NoUser

    def __init__(self, source: Source, user_id: str):
        if not source or not user_id:
            raise ValueError("source or user_id can't be blank")
        self.source = source
        self.user_id = user_id
        self.uid: str = ""

    @property
    def key(self) -> str:
        """ Key used as part of database IDs """
        return f"{self.source.value}:{self.user_id}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key})"
