""" Test quest data """

import pytest
from firebase_utils import db
from quest_page import QuestPage
from quest import DEBUG_QUEST_NAME, QuestError, QuestLoadError


def test_quest_fail(testing_game):
    """ Try to load a non-existant quest """
    with pytest.raises(QuestError):
        QuestPage.from_game_get_quest(testing_game, "_does not exist_")


def test_bad_key():
    with pytest.raises(ValueError):
        QuestPage.make_key(None, None)


def test_get_quest(testing_game):
    """ A successful class fetch """
    quest = QuestPage.from_game_get_quest(testing_game, DEBUG_QUEST_NAME)

    assert str(quest)
    assert repr(quest)

    assert quest.quest.__class__.__name__ == DEBUG_QUEST_NAME

    assert str(quest.quest)
    assert repr(quest.quest)


def test_quest_load_fail(testing_quest_page):
    """ Test loading fail """

    # create new game
    testing_quest_page.save()

    # break the data
    testing_quest_page.doc_ref.set({"this": "broken"})

    with pytest.raises(QuestLoadError):
        testing_quest_page.load()

    # cleanup
    testing_quest_page.delete()


def test_quest(testing_game):
    """ Test creating a valid quest """

    # create new game
    quest = QuestPage.from_game_get_quest(testing_game, DEBUG_QUEST_NAME)

    # check the quest doesn't exist before
    assert not quest.exists

    quest.save()

    # check it
    assert quest.exists
