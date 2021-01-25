""" Test for quest load/save handling system """

import json
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


def test_quest_load_version_fail(testing_game):
    """ Tests a quest load fail due to semver mismatch """

    quest = DebugQuest.new(testing_game)

    # generate a save data and make bad
    storage_model = quest.get_storage_model()
    storage_model.version = str(DebugQuest.version.bump_major())

    # try to load with the bad version
    with pytest.raises(QuestLoadError):
        quest.load_storage_model(storage_model)


def test_quest_load_data_fail(testing_game):
    """ Tests a quest load fail due to data model mismatch """

    quest = DebugQuest.new(testing_game)

    # generate a save data and make bad
    storage_model = quest.get_storage_model()
    storage_model.serialized_data = json.dumps({"this": "nonesense"})

    # try to load with the bad data
    with pytest.raises(QuestLoadError):
        quest.load_storage_model(storage_model)


def test_quest_load_save(testing_game):
    """ Tests a successful load with matching semvar """

    quest = DebugQuest.new(testing_game)

    # generate a save data and edit a bit
    storage_model = quest.get_storage_model()
    storage_model.completed_stages = [DebugQuest.Start.__name__]

    # create a new game and load the good version
    quest.load_storage_model(storage_model)

    # check it
    check_model = quest.get_storage_model()
    assert check_model.completed_stages == storage_model.completed_stages
