""" Base Classes for quest objects """
from __future__ import annotations

from typing import List, Dict, ClassVar, Type, Union, cast
from enum import Enum
from abc import ABC, abstractmethod
from inspect import isclass
from graphlib import TopologicalSorter, CycleError

from pydantic import BaseModel, Field, ValidationError
from semver import VersionInfo  # type:  ignore

from app.game import Game, NoGame, NoGameType
from app.firebase_utils import db
from .exceptions import QuestError, QuestLoadError, QuestDefinitionError
from .stage import Stage


def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False

    return True


class QuestBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class StorageModel(QuestBaseModel):
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
    ######
    # Factory methods
    ######
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
        quest.quest_data = cls.QuestDataModel()
        quest.game = game
        return quest

    ######
    # ABC
    ######
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
    def Start(cls) -> Type[Stage]:
        """ The first quest """
        return NotImplemented

    @property
    @abstractmethod
    def stages(cls) -> Dict[str, Type[Stage]]:
        """ The initial default data to start quests with """
        return NotImplemented

    # default, overridable model is empty pydantic model
    QuestDataModel: ClassVar[Type[QuestBaseModel]] = QuestBaseModel

    def __init_subclass__(cls):
        """ Subclasses instantiate by copying default data """
        # build class list
        cls.stages = {}
        for name, class_var in vars(cls).items():
            if isclass(class_var) and issubclass(class_var, Stage):
                cls.stages[name] = class_var

    ######
    # Runtime methods
    ######

    # loaded player quest data
    quest_data: QuestBaseModel = QuestBaseModel()
    completed_stages: List[str] = []
    graph: TopologicalSorter = TopologicalSorter()

    # the game
    game: Union[Game, NoGameType] = NoGame

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

    def load_stages(self) -> None:
        """ loads the stages """

        # load graph
        self.graph = TopologicalSorter()
        for stage_name, StageClass in self.stages.items():
            for child_name in cast(List[str], StageClass.children):
                if child_name not in self.stages:
                    raise QuestDefinitionError(
                        f"Quest does not have stage named '{child_name}'"
                    )
                self.graph.add(child_name, stage_name)

        try:
            self.graph.prepare()
        except CycleError as err:
            raise QuestDefinitionError(
                f"Quest {self.__class__.__name__} prepare failed! {err}"
            ) from err

    def __repr__(self):
        return f"{self.__class__.__name__}(game={repr(self.game)})"
