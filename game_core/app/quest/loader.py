""" Dynamically load quest data """

from __future__ import annotations
from typing import Dict, Type
import pkgutil
import importlib
import inspect
from pathlib import Path

from .exceptions import QuestError
from .quests.intro import IntroQuest
from .quests.debug import DebugQuest
from .quest import Quest, Difficulty

FIRST_QUEST_KEY = "__FIRST__"
DEBUG_QUEST_KEY = "__DEBUG__"

all_quests: Dict[str, Type[Quest]] = {
    FIRST_QUEST_KEY: IntroQuest,
    DEBUG_QUEST_KEY: DebugQuest,
}

for _, module_name, _ in pkgutil.iter_modules(
    path=[str(Path(__file__).parent / "quests")]
):
    module = importlib.import_module(".quests." + module_name, __package__)
    classes = inspect.getmembers(module, inspect.isclass)

    for parent, QuestClass in classes:
        if (
            Quest in QuestClass.__bases__
            and QuestClass.difficulty != Difficulty.RESERVED
        ):
            if QuestClass.__name__ in all_quests:
                raise ValueError(
                    f"Duplicate quests found with name {QuestClass.__name__}"
                )  # pragma: no cover
            all_quests[QuestClass.__name__] = QuestClass


def get_quest_by_name(name: str) -> Type[Quest]:
    try:
        return all_quests[name]
    except KeyError as err:
        raise QuestError(f"No quest name {name}") from err


def get_first_quest() -> Type[Quest]:
    return get_quest_by_name(FIRST_QUEST_KEY)
