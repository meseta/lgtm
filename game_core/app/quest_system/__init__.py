import os
import pkgutil
import importlib

from .exceptions import QuestError, QuestLoadError
from .quest_system import Quest, Difficulty

from .quests import all_quests


def get_quest_by_name(name: str) -> Quest:
    if name in all_quests:
        return all_quests[name]
    raise NotImplemented(f"No quest name {name}")
