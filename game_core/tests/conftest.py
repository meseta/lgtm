""" Setup for tests """

import pytest
import string
import random

from firebase_utils import db, firestore
from user import User, Source, UserData
from game import Game
from quest_page import QuestPage
from quest import DEBUG_QUEST_NAME


@pytest.fixture
def random_id():
    """ A random alphanumeric ID for various uses in tests """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


@pytest.fixture(scope="package")
def testing_user_data():
    user_id = "test_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )
    return UserData(
        profileImage="",
        name="Test User",
        handle="test_user",
        id=user_id,
        accessToken="",
    )


@pytest.fixture(scope="package")
def testing_user(testing_user_data):
    """ A user for testing, that can have games assigned, cleans up afterwards """

    uid = testing_user_data.id

    user = User.new_from_data(uid, Source.TEST, testing_user_data)
    yield user


@pytest.fixture(scope="package")
def testing_game(testing_user):
    """ A random game for testing, cleans up afterwards """
    fork_url = "url_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )

    game = Game.from_user(testing_user)
    game.set_fork_url(fork_url)
    game.save()
    yield game


@pytest.fixture
def testing_quest_page(testing_game):
    """ A random quest for testing, cleans up afterwards """
    quest = QuestPage.from_game_get_quest(testing_game, DEBUG_QUEST_NAME)
    yield quest
