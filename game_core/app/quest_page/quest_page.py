""" Base Classes for quest objects """
from __future__ import annotations
from typing import Generator
from structlog import get_logger

from orm import Orm, OrmNotFound
from game import Game

from quest import Quest, FIRST_QUEST_NAME, QuestLoadError
from tick import TickType
from .models import QuestData

logger = get_logger(__name__)


class QuestPage(Orm, collection="quest", parent_orm=Game):
    data: QuestData
    storage_model = QuestData
    quest: Quest

    @staticmethod
    def make_key(game: Game, quest_name: str) -> str:
        if not quest_name:
            raise ValueError("quest_name must be valid")
        return f"{game.key}:{quest_name}"

    @classmethod
    def from_game_get_first_quest(cls, game: Game) -> QuestPage:
        return cls.from_game_get_quest(game, FIRST_QUEST_NAME)

    @classmethod
    def from_game_get_quest(cls, game: Game, quest_name: str) -> QuestPage:
        key = cls.make_key(game, quest_name)
        quest = cls(key, quest_name)
        quest.parent_key = game.key
        return quest

    @classmethod
    def iterate_all(cls) -> Generator[QuestPage, None, None]:
        """ Iterate over all quests, the generator yields loaded quest_pages """
        docs = cls.col_ref.where("complete", "!=", True).stream()
        for doc in docs:
            data = cls.storage_model.parse_obj(doc.to_dict())
            quest_page = cls(doc.id, data.quest_name)
            quest_page.load()
            yield quest_page

    def __init__(self, key: str, quest_name: str):
        super().__init__(key)
        self.quest = Quest.from_name(quest_name, self)
        self.data.quest_name = quest_name

    @property
    def game(self) -> Union[Game, OrmNotFound]:
        """ Parent object is Game """
        return self.parent

    def load(self) -> None:
        """ Additionally parse the quest storage """
        super().load()
        if isinstance(self.quest, Quest):
            self.quest.load_raw(self.data.version, self.data.serialized_data)

    def save(self) -> None:
        """ Additionally parse out the quest storage """
        if isinstance(self.quest, Quest):
            self.data.serialized_data = self.quest.save_raw()
            self.data.version = str(self.quest.version)
        super().save()

    def execute(self, tick_type: TickType = TickType.FULL) -> None:
        """ Execute """
        self.quest.execute(tick_type)

    def mark_stage_complete(self, stage_name: str) -> None:
        """ Mark a stage as completed """
        if stage_name not in self.data.completed_stages:
            self.data.completed_stages.append(stage_name)

    def is_stage_complete(self, stage_name: str) -> bool:
        """ Returns whether stage is completed """
        return stage_name in self.data.completed_stages

    def mark_quest_complete(self) -> None:
        """ Mark the quest as complete """
        self.data.complete = True

    def is_quest_complete(self) -> bool:
        """ Returns whether the quest is complete """
        return self.data.complete
