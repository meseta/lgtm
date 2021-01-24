""" Dynamically load quest data """

from __future__ import annotations
from typing import Dict, Type, TYPE_CHECKING
import os
import pkgutil
import importlib
import inspect
from pathlib import Path

from .quests.intro import IntroQuest
from .quests.debug import DebugQuest
from .quest import Quest

FIRST_QUEST_KEY = "__FIRST__"
DEBUG_QUEST_KEY = "__DEBUG__"

all_quests: Dict[str, Type[Quest]] = {
    FIRST_QUEST_KEY: IntroQuest,
    DEBUG_QUEST_KEY: DebugQuest,
}

for _, module_name, _ in pkgutil.iter_modules(path=[Path(__file__) / "quests"]):
    module = importlib.import_module(".quests." + module_name, __package__)
    classes = inspect.getmembers(module, inspect.isclass)

    for parent, QuestClass in classes:
        if Quest in QuestClass.__bases__:
            if QuestClass.__name__ in all_quests:
                raise ValueError(
                    f"Duplicate quests found with name {QuestClass.__name__}"
                )  # pragma: no cover
            all_quests[QuestClass.__name__] = QuestClass
