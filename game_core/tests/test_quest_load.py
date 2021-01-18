""" Tests for quests """
import pytest
from copy import deepcopy
from semver import VersionInfo

from app.quest_system import QuestLoadError
from app.quest_system.quests.debug import DebugQuest


def test_quest_load_fail():
    """ Tests a quest load fail due to semver mismatch """

    # generate a bad save data version
    save_data = deepcopy(DebugQuest.default_data)
    save_data[DebugQuest.VERSION_KEY] = str(DebugQuest.version.bump_major())

    # create a new game and try to load with the bad version
    quest = DebugQuest()
    with pytest.raises(QuestLoadError):
        quest.load(save_data)


def test_quest_load_save():
    """ Tests a successful load with matching semvar """

    # generate save data version
    save_data = deepcopy(DebugQuest.default_data)
    save_data[DebugQuest.VERSION_KEY] = str(DebugQuest.version)

    # create a new game and load the good version
    quest = DebugQuest()
    quest.load(save_data)
    assert quest.get_save_data() == save_data
