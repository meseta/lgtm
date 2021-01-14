""" Tests for quests """
import pytest
from semver import VersionInfo

from app.quests import QuestLoadError
from app.quests.quest import Quest, semver_safe, VERSION_KEY

@pytest.fixture
def quest():
    return Quest("2.2.2", {"a": 1})

# pylint: disable=redefined-outer-name
@pytest.mark.parametrize("start, dest", [
    ("1.1.1", "1.1.2"), # patch increment is ok
    ("1.1.2", "1.1.1"), # patch decrement is ok
    ("1.1.1", "1.2.1"), # minor increment is ok
    ("1.1.1", "1.2.2"), # minor+patch bump is ok
    ("1.1.2", "1.2.1"), # minor+patch bump is ok
])
def test_semver_safe(start, dest):
    """ Tests semver safe loading"""

    start = VersionInfo.parse(start)
    dest = VersionInfo.parse(dest)
    assert semver_safe(start, dest) == True

@pytest.mark.parametrize("start, dest", [
    ("2.1.1", "1.1.1"), # major increment not safe
    ("1.1.1", "2.1.1"), # major decement not safe
    ("1.2.1", "1.1.1"), # minor decrement not safe (no forward compatibility guarantee)
])
def test_semver_unsafe(start, dest):
    """ Tests semver unsafe loading"""

    start = VersionInfo.parse(start)
    dest = VersionInfo.parse(dest)
    assert semver_safe(start, dest) == False

def test_quest_load_fail(quest):
    """ Tests a quest load fail due to semver mismatch """

    bad_version_quest_data = {
        VERSION_KEY: "1.2.2",
        "a": 2
    }
    with pytest.raises(QuestLoadError):
        quest.load(bad_version_quest_data)

def test_quest_load_save(quest):
    """ Tests a quest load fail due to semver mismatch """

    quest_data = {
        VERSION_KEY: "2.1.1",
        "a": 2
    }

    quest.load(quest_data)
    assert quest.update_save_data()["a"] == quest_data["a"]
    