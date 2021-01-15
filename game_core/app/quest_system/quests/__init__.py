import os
import pkgutil
import importlib

all_quests = {}
for _importer, _name, _ in pkgutil.iter_modules(path=[os.path.dirname(__file__)]):
    _module = importlib.import_module("." + _name, __package__)
    _quest = _module.quest

    if _quest.name in all_quests:
        raise Exception(f"{_quest.name} was registered twice!")

    all_quests[_quest.name] = _quest
