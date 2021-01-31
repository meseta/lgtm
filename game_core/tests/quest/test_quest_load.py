""" Test for quest load/save handling system """

import json
import pytest
from semver import VersionInfo

from quest import Quest, QuestError, QuestLoadError, QuestSaveError
from quest.quest import semver_safe
from quest.quests.debug import DebugQuest

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


def test_quest_load_version_fail(testing_quest):
    """ Tests a quest load fail due to semver mismatch """

    # generate a save data and make bad
    storage_model = testing_quest.get_storage_model()
    storage_model.version = str(DebugQuest.version.bump_major())

    # try to load with the bad version
    with pytest.raises(QuestLoadError):
        testing_quest.load_storage_model(storage_model)


def test_quest_load_data_fail(testing_quest):
    """ Tests a quest load fail due to data model mismatch """

    # generate a save data and make bad
    storage_model = testing_quest.get_storage_model()
    storage_model.serialized_data = json.dumps({"this": "nonesense"})

    # try to load with the bad data
    with pytest.raises(QuestLoadError):
        testing_quest.load_storage_model(storage_model)


def test_quest_load_save(testing_quest):
    """ Tests a successful load with matching semvar """

    # generate a save data and edit a bit
    storage_model = testing_quest.get_storage_model()
    storage_model.completed_stages = [DebugQuest.Start.__name__]

    # create a new game and load the good version
    testing_quest.load_storage_model(storage_model)

    # check it
    check_model = testing_quest.get_storage_model()
    assert check_model.completed_stages == storage_model.completed_stages
