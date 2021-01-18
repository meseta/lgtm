""" This file fetches every class whose base class is Quest from the other
files in the directory """

from typing import Type
import os
import pkgutil
import importlib
import inspect

from ..system import Quest
from ..exceptions import QuestError

all_quests = {}
for _importer, _name, _ in pkgutil.iter_modules(path=[os.path.dirname(__file__)]):
    _module = importlib.import_module("." + _name, __package__)
    _classes = inspect.getmembers(_module, inspect.isclass)

    for _parent, _class in _classes:
        if Quest in _class.__bases__:
            if _class.__name__ in all_quests:
                raise ValueError(f"Duplicate quests found with name {_class.__name__}")
            all_quests[_class.__name__] = _class

def get_quest_by_name(name: str) -> Type[Quest]:
    try:
        return all_quests[name]
    except KeyError as err:
        raise QuestError(f"No quest name {name}") from err
