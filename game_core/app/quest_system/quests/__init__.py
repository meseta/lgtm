import os
import pkgutil
import importlib
import inspect

from ..quest_system import Quest

all_quests = {}
for _importer, _name, _ in pkgutil.iter_modules(path=[os.path.dirname(__file__)]):
    _module = importlib.import_module("." + _name, __package__)
    _classes = inspect.getmembers(_module, inspect.isclass)

    for _parent, _class in _classes:
        if Quest in _class.__bases__:
            all_quests[_class.__name__] = _class
