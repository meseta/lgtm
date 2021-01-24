""" Test for quest load/save handling system """

import json
from copy import deepcopy
import pytest
from semver import VersionInfo

from app.quest import Quest, QuestError, QuestLoadError, QuestSaveError
from app.quest.quest import semver_safe
from app.quest.quests.debug import DebugQuest

# pylint: disable=redefined-outer-name
@pytest.mark.parametrize(
    "start, dest",
    [
        ("1.1.1", "1.1.2"),  # patch increment is ok
        ("1.1.2", "1.1.1"),  # patch decrement is ok
        ("1.1.1", "1.2.1"),  # minor increment is ok
        ("1.1.1", "1.2.2"),  # minor+patch bump is ok
        ("1.1.2", "1.2.1"),  # minor+patch bump is ok
    ],
)
def test_semver_safe(start, dest):
    """ Tests semver safe loading"""

    start = VersionInfo.parse(start)
    dest = VersionInfo.parse(dest)
    assert semver_safe(start, dest) == True


@pytest.mark.parametrize(
    "start, dest",
    [
        ("2.1.1", "1.1.1"),  # major increment not safe
        ("1.1.1", "2.1.1"),  # major decement not safe
        ("1.2.1", "1.1.1"),  # minor decrement not safe
    ],
)
def test_semver_unsafe(start, dest):
    """ Tests semver unsafe loading"""

    start = VersionInfo.parse(start)
    dest = VersionInfo.parse(dest)
    assert semver_safe(start, dest) == False


def test_quest_load_version_fail():
    """ Tests a quest load fail due to semver mismatch """

    # generate a bad save data version
    save_data = DebugQuest.default_data.json()
    bad_version = str(DebugQuest.version.bump_major())

    # try to load with the bad version
    quest = DebugQuest()
    with pytest.raises(QuestLoadError):
        quest.load_save_data(save_data, bad_version)


def test_quest_load_data_fail():
    """ Tests a quest load fail due to data model mismatch """

    # generate a bad save data version
    save_data = json.dumps({"this": "nonesense"})
    save_version = str(DebugQuest.version)

    # try to load with the bad version
    quest = DebugQuest()
    with pytest.raises(QuestLoadError):
        quest.load_save_data(save_data, save_version)


def test_quest_load_save():
    """ Tests a successful load with matching semvar """

    # generate save data version
    save_data = DebugQuest.default_data.json()
    save_version = str(DebugQuest.version)

    # create a new game and load the good version
    quest = DebugQuest()
    quest.load_save_data(save_data, save_version)
    assert json.loads(quest.get_save_data()).items() >= json.loads(save_data).items()
