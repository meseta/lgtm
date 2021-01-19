""" This file fetches every class whose base class is Quest from the other
files in the directory """

from typing import Dict, Type
import os
import pkgutil
import importlib
import inspect

from ..quest import Quest
from .intro import IntroQuest
from .debug import DebugQuest

FIRST_QUEST_KEY = "__FIRST__"
DEBUG_QUEST_KEY = "__DEBUG__"

all_quests: Dict[str, Type[Quest]] = {
    FIRST_QUEST_KEY: IntroQuest,
    DEBUG_QUEST_KEY: DebugQuest,
}

for _, module_name, _ in pkgutil.iter_modules(path=[os.path.dirname(__file__)]):
    module = importlib.import_module("." + module_name, __package__)
    classes = inspect.getmembers(module, inspect.isclass)

    for parent, QuestClass in classes:
        if Quest in QuestClass.__bases__:
            if QuestClass.__name__ in all_quests:
                raise ValueError(
                    f"Duplicate quests found with name {quest.__name__}"
                )  # pragma: no cover
            all_quests[QuestClass.__name__] = QuestClass

__all__ = ["all_quests", "FIRST_QUEST_KEY", "DEBUG_QUEST_KEY"]
