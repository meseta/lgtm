""" Test for quest load/save handling system """

import json
import pytest

from semver import VersionInfo
from quest import QuestLoadError


def test_quest_load_version_fail(testing_quest_page):
    """ Tests a quest load fail due to semver mismatch """
    testing_quest_page.save()

    # fetch the data
    doc = testing_quest_page.doc_ref.get()
    data = testing_quest_page.storage_model.parse_obj(doc.to_dict())

    # mess with the version
    data.version = str(VersionInfo.parse(data.version).bump_major())
    testing_quest_page.doc_ref.set(data.dict())

    # try to load with the bad version
    with pytest.raises(QuestLoadError):
        testing_quest_page.load()

    # cleanup
    testing_quest_page.delete()


def test_quest_load_data_fail(testing_quest_page):
    """ Tests a quest load fail due to data model mismatch """
    testing_quest_page.save()

    # fetch the data
    doc = testing_quest_page.doc_ref.get()
    data = testing_quest_page.storage_model.parse_obj(doc.to_dict())

    # mess with the data
    data.serialized_data = json.dumps({"this": "nonesense"})
    testing_quest_page.doc_ref.set(data.dict())

    # try to load with the bad version
    with pytest.raises(QuestLoadError):
        testing_quest_page.load()

    # cleanup
    testing_quest_page.delete()


def test_quest_load_save(testing_quest_page):
    """ Tests a successful load with matching semvar """

    # generate a save data and edit a bit
    testing_quest_page.delete()
    assert not testing_quest_page.exists

    testing_quest_page.save()
    assert testing_quest_page.exists

    testing_quest_page.load()
