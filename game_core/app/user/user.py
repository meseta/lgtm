""" User entity management, note: User entities in firestore are not necessary auth users """

from __future__ import annotations
from typing import Union

from orm import Orm
from .models import UserData, Source
from .sentinels import NoUidType, NoUid


class User(Orm, collection="user"):
    data: UserData
    storage_model = UserData

    @staticmethod
    def make_key(source: Source, user_id: str) -> str:
        """ Key used as part of database IDs """
        return f"{source.value}:{user_id}"

    @classmethod
    def from_source_id(cls, source: Source, user_id: str) -> User:
        """ Create a user from the source+id """
        key = cls.make_key(source, user_id)
        user = cls(key)
        user.load()
        return user

    @classmethod
    def new_from_data(cls, uid: str, source: Source, user_data: UserData) -> User:
        """ Save user to database """

        user = cls.from_source_id(source, user_data.id)
        user.parent_key = uid
        user.data = user_data
        user.save()
        return user

    @property
    def uid(self) -> Union[str, NoUidType]:
        """ UID is parent key in this ORM, if it exists """
        if isinstance(self.parent_key, str):
            return self.parent_key
        return NoUid
