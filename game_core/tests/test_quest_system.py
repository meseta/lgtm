""" Tests for quests """
import pytest
from semver import VersionInfo

from app.quest_system import QuestError, get_quest_by_name, all_quests
from app.quest_system.system import semver_safe
from app.quest_system.quests.debug import DebugQuest

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
    """ Try to load a non-existant class """
    with pytest.raises(QuestError):
        get_quest_by_name("_does not exist_")


def test_get_quest():
    """ A successful class fetch """
    assert get_quest_by_name(DebugQuest.__name__) == DebugQuest


def test_all_quest_subclasses():
    """ Instantiate all quests to check abstract base class implementation """

    for quest_class in all_quests.values():
        quest_class()  # should succeed if correctly implemented
