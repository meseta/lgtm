""" ORM wrapper around firebase """

from __future__ import annotations
from typing import ClassVar, Type, Union, Any, Generator, Dict
from abc import ABC, abstractmethod
from pydantic import BaseModel

from google.cloud.firestore_v1.document import DocumentReference  # type: ignore
from google.cloud.firestore_v1.collection import CollectionReference  # type: ignore
from firebase_utils import db, firestore

from .sentinels import (
    NoParentType,
    NoParent,
    OrmNotFoundType,
    OrmNotFound,
    DocRefNotFoundType,
    DocRefNotFound,
    NoKeyType,
    NoKey,
)


class Orm(ABC):
    """ ORM base class links stuff together """

    # @classmethod
    # def query_one(
    #     cls, query_field: str, operator: str, value: Any
    # ) -> Union[Orm, OrmNotFoundType]:
    #     """ Queries for one object """
    #     for doc in cls.query_all(query_field, operator, value):
    #         return doc
    #     return OrmNotFound

    # @classmethod
    # def query_all(
    #     cls, query_field: str, operator: str, value: Any
    # ) -> Generator[Orm, None, None]:
    #     """ Generator to iterate over all objects matching query """
    #     docs = (
    #         db.collection(cls.collection).where(query_field, operator, value).stream()
    #     )
    #     for doc in docs:
    #         obj = cls(doc.id)
    #         obj.load_storage_model(doc.to_dict())
    #         yield obj

    @property
    @abstractmethod
    def storage_model(cls) -> Type[BaseModel]:
        """ Storage model """
        return NotImplemented

    collection: ClassVar[str]
    parent_orm: ClassVar[Union[Type[Orm], NoParentType]]
    col_ref: CollectionReference

    def __init_subclass__(
        cls, collection: str, parent_orm: Union[Type[Orm], NoParentType] = NoParent
    ):
        """ Set collection and parent """
        cls.collection = collection
        cls.parent_orm = parent_orm
        cls.col_ref = db.collection(collection)

    key: Union[str, NoKeyType]
    parent_key: Union[str, NoKeyType]
    data: BaseModel

    def __init__(self, key: Union[str, NoKeyType] = NoKey):
        self.key = key
        self.data = self.storage_model()
        self.parent_key = NoKey

    @property
    def parent(self) -> Union[Orm, OrmNotFoundType]:
        if self.parent_orm is not NoParent and self.parent_key is not NoKey:
            return self.parent_orm(self.parent_key)

        return OrmNotFound

    @property
    def doc_ref(self) -> Union[DocumentReference, DocRefNotFoundType]:
        """ Return database docreference """
        if self.key is NoKey:
            return DocRefNotFound
        else:
            return self.col_ref.document(self.key)

    @property
    def exists(self) -> bool:
        """ Whether object exists in the database """
        doc_ref = self.doc_ref
        if isinstance(doc_ref, DocumentReference):
            return doc_ref.get().exists
        return False

    def load(self) -> None:
        """ Load data from database """
        doc_ref = self.doc_ref
        if not isinstance(doc_ref, DocumentReference):
            return

        doc = doc_ref.get()
        if doc.exists:
            self.load_storage_model(doc.to_dict())

    def load_storage_model(self, data: dict) -> None:
        """ Load the data from dict """
        if "parent_key" in data:
            self.parent_key = (
                data["parent_key"] if data["parent_key"] is not None else NoKey
            )
            del data["parent_key"]

        self.data = self.storage_model.parse_obj(data)

    def get_storage_model(self) -> Dict[str, Any]:
        """ Get the data as a dict """
        return self.data.dict()

    def save(self):
        doc_data = {
            **self.get_storage_model(),
            "parent_key": self.parent_key if self.parent_key is not NoKey else None,
        }

        if self.exists:
            doc_data["updated"] = firestore.SERVER_TIMESTAMP
            self.doc_ref.set(doc_data, merge=True)
        else:
            doc_data["created"] = firestore.SERVER_TIMESTAMP

            if self.key is NoKey:
                _, doc = self.col_ref.add(doc_data)
                self.key = doc.id
            else:
                doc = self.doc_ref.set(doc_data)

    def delete(self):
        doc_ref = self.doc_ref
        if not isinstance(doc_ref, DocumentReference):
            return
        doc_ref.delete()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.key})"
