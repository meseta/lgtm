""" Base Classes for quest objects """
from __future__ import annotations

from typing import Any, List, Dict, ClassVar, Type, Union
from enum import Enum
from abc import ABC, abstractmethod
from inspect import isclass

from pydantic import BaseModel, Field, create_model, ValidationError
from semver import VersionInfo  # type:  ignore

from app.game import Game, NoGame
from app.firebase_utils import db
from .exceptions import QuestError, QuestLoadError, QuestSaveError
from .stage import Stage
from .sentinels import NoData, NoQuest


def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False

    return True


class StorageModel(BaseModel):
    version: str = Field(..., title="Version number to control loading")
    completed_stages: List[str] = Field([], title="List of completed stage names")
    serialized_data: str = Field(..., title="Serialized save data")


class Difficulty(Enum):
    RESERVED = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    HACKER = 5


class Quest(ABC):
    @classmethod
    def get_by_name(cls, name: str) -> Type[Quest]:
        from .loader import all_quests  # avoid circular import

        try:
            return all_quests[name]
        except KeyError as err:
            raise QuestError(f"No quest name {name}") from err

    @classmethod
    def get_first(cls) -> Type[Quest]:
        from .loader import FIRST_QUEST_KEY  # avoid circular import

        return cls.get_by_name(FIRST_QUEST_KEY)

    @classmethod
    def new(cls, game: Game) -> Quest:
        """ create a new quest whose parent is `game` """
        if not game:
            raise ValueError("Game can't be blank")

        quest = cls()
        quest.quest_data = cls.default_data.copy(deep=True)
        quest.game = game
        return quest

    @property
    @abstractmethod
    def version(cls) -> VersionInfo:
        """ The version of this quest, used to check against load data """
        return NotImplemented

    @property
    @abstractmethod
    def difficulty(cls) -> Difficulty:
        """ Difficulty metadata, for display purposes only """
        return NotImplemented

    @property
    @abstractmethod
    def description(cls) -> str:
        """ Quest description metadata, for display purposes only """
        return NotImplemented

    @property
    @abstractmethod
    def QuestDataModel(cls) -> Type[BaseModel]:
        """ Pydantic model for loading and saving quest data values """
        return NotImplemented

    @property
    @abstractmethod
    def Start(cls) -> Type[Stage]:
        """ The first quest """
        return NotImplemented

    # the initial default data to start quests with
    default_data: ClassVar[BaseModel] = NoData()

    # dynamically generated stages
    stages: ClassVar[Dict[str, Type[Stage]]] = {}

    def __init_subclass__(cls):
        """ Subclasses instantiate by copying default data """
        # build class list
        for name, class_var in vars(cls).items():
            if isclass(class_var) and issubclass(class_var, Stage):
                cls.stages[name] = class_var
                class_var()

    # loaded player quest data
    quest_data: BaseModel = NoData()
    completed_stages: List[str] = []

    # the game
    game: Union[Game, Type[NoGame]] = NoGame

    @property
    def key(self) -> str:
        """ Key for referencing in database """
        if isinstance(self.game, Game):
            return f"{self.game.key}:{self.__class__.__name__}"
        raise AttributeError("game parent not valid")

    def load(self) -> None:
        """ Load data from storage """
        quest_doc = db.collection("quest").document(self.key).get()

        if quest_doc.exists:
            try:
                storage_model = StorageModel.parse_obj(quest_doc.to_dict())
            except ValidationError as err:
                raise QuestLoadError(f"Storage model validation error! {err}") from err

            self.load_storage_model(storage_model)

    def save(self) -> None:
        """ Save data to storage """

        quest_ref = db.collection("quest").document(self.key)
        quest_ref.set(self.get_storage_model().dict())

    def load_storage_model(self, storage_model: StorageModel) -> None:
        """ Load save data back into structure """

        # check save version is safe before upgrading
        save_semver = VersionInfo.parse(storage_model.version)
        if not semver_safe(save_semver, self.version):
            raise QuestLoadError(
                f"Unsafe version mismatch! {save_semver} -> {self.version}"
            )

        try:
            self.quest_data = self.QuestDataModel.parse_raw(
                storage_model.serialized_data
            )
        except ValidationError as err:
            raise QuestLoadError(f"Quest data validation error! {err}") from err

        self.completed_stages = storage_model.completed_stages

    def get_storage_model(self) -> StorageModel:
        """ Updates save data with new version and output """
        return StorageModel(
            version=str(self.version),
            completed_stages=self.completed_stages,
            serialized_data=self.quest_data.json(),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(game={repr(self.game)})"
