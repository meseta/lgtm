""" Test for quest load/save handling system """

import pytest
from semver import VersionInfo
from quest import DEBUG_QUEST_NAME
from quest.quest import semver_safe


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
    """ Tests semver unsafe loading """

    start = VersionInfo.parse(start)
    dest = VersionInfo.parse(dest)
    assert semver_safe(start, dest) == False
