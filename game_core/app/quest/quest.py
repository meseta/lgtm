""" Base Classes for quest objects """
from __future__ import annotations

from typing import Any, List, Dict, ClassVar, Type, Optional
from enum import Enum
from abc import ABC, abstractmethod
from copy import deepcopy
from inspect import isclass

from pydantic import BaseModel, create_model, ValidationError
from semver import VersionInfo  # type:  ignore

from app.game import Game
from app.firebase_utils import db
from .exceptions import QuestError, QuestLoadError, QuestSaveError
from .stage import Stage


def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False

    return True


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
        quest.quest_data = deepcopy(cls.default_data)
        quest.game = game

        # load data if it exists, and then save data to upgrade version
        quest.load()
        quest.save()

        return quest

    @property
    @abstractmethod
    def version(cls) -> VersionInfo:
        return NotImplemented

    @property
    @abstractmethod
    def difficulty(cls) -> Difficulty:
        return NotImplemented

    @property
    @abstractmethod
    def description(cls) -> str:
        return NotImplemented

    @property
    @abstractmethod
    def QuestDataModel(cls) -> Type[BaseModel]:
        return NotImplemented

    @property
    @abstractmethod
    def default_data(cls) -> BaseModel:
        return NotImplemented

    stages: Dict[str, Type[Stage]] = {}

    def __init_subclass__(cls):
        """ Subclasses instantiate by copying default data """
        # build class list
        for name, class_var in vars(cls).items():
            if isclass(class_var) and issubclass(class_var, Stage):
                cls.stages[name] = class_var

    quest_data: Optional[BaseModel] = None
    game: Optional[Game] = None

    @property
    def key(self) -> str:
        if not self.game:
            raise ValueError("game parent not set")
        return f"{self.game.key}:{self.__class__.__name__}"

    def load(self) -> None:
        """ Load data from bucket """
        quest_doc = db.collection("quest").document(self.key).get()

        if quest_doc.exists:
            quest_dict = quest_doc.to_dict()
            if "data" in quest_dict and "version" in quest_dict:
                self.load_save_data(quest_dict["data"], quest_dict["version"])

    def save(self) -> None:
        """ Save data to storage """

        quest_ref = db.collection("quest").document(self.key)
        quest_ref.set(
            {
                "data": self.get_save_data(),
                "version": str(self.version),
            }
        )

    def load_save_data(self, save_data: str, version: str) -> None:
        """ Load save data back into structure """

        # check save version is safe before upgrading
        save_semver = VersionInfo.parse(version)
        if not semver_safe(save_semver, self.version):
            raise QuestLoadError(
                f"Unsafe version mismatch! {save_semver} -> {self.version}"
            )

        try:
            self.quest_data = self.QuestDataModel.parse_raw(save_data)
        except ValidationError as err:
            raise QuestLoadError(f"Quest data validation error! {err}") from err

    def get_save_data(self) -> str:
        """ Updates save data with new version and output """
        return self.quest_data.json()

    def __repr__(self):
        return f"{self.__class__.__name__}(game={repr(self.game)})"
