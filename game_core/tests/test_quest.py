""" Tests for quests """
import pytest
from semver import VersionInfo

from app.quest_system import QuestError, QuestLoadError, get_quest_by_name
from app.quest_system.quest_system import semver_safe, VERSION_KEY
from app.quest_system.quests.debug import DebugQuest


@pytest.fixture
def DebugQuest():
    return get_quest_by_name(DebugQuest.__name__)


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
        (
            "1.2.1",
            "1.1.1",
        ),  # minor decrement not safe (no forward compatibility guarantee)
    ],
)
def test_semver_unsafe(start, dest):
    """ Tests semver unsafe loading"""

    start = VersionInfo.parse(start)
    dest = VersionInfo.parse(dest)
    assert semver_safe(start, dest) == False


def test_quest_class_fail():
    with pytest.raises(QuestError):
        get_quest_by_name("_does not exist_")


def test_quest_load_fail(DebugQuest):
    """ Tests a quest load fail due to semver mismatch """

    quest = DebugQuest()

    bad_version_quest_data = {VERSION_KEY: "1.2.2", "a": 2}
    with pytest.raises(QuestLoadError):
        quest.load(bad_version_quest_data)


def test_quest_load_save(DebugQuest):
    """ Tests a quest load fail due to semver mismatch """

    quest = DebugQuest()

    quest_data = {VERSION_KEY: "1.0.0", "a": 2}
    quest.load(quest_data)
    assert quest.get_save_data()["a"] == quest_data["a"]
