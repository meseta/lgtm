""" Dynamically load quest data """

from __future__ import annotations
from typing import Dict, Type
import pkgutil
import importlib
import inspect
from pathlib import Path

from .content.intro import IntroQuest
from .content.debug import DebugQuest
from .quest import Quest
from .exceptions import QuestDefinitionError

FIRST_QUEST_NAME = IntroQuest.__name__
DEBUG_QUEST_NAME = DebugQuest.__name__

all_quests: Dict[str, Type[Quest]] = {}

for _, module_name, _ in pkgutil.iter_modules(
    path=[str(Path(__file__).parent / "content")]
):
    module = importlib.import_module(".content." + module_name, __package__)
    classes = inspect.getmembers(module, inspect.isclass)

    for parent, QuestClass in classes:
        if Quest in QuestClass.__bases__:
            if QuestClass.__name__ in all_quests:
                raise QuestDefinitionError(
                    f"Duplicate quests found with name {QuestClass.__name__}"
                )  # pragma: no cover
            all_quests[QuestClass.__name__] = QuestClass
