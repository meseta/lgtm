""" Setup for tests """

import pytest
import string
import random

from app.firebase_utils import db, firestore
from app.user import User, Source
from app.game import Game
from app.quest import Quest, DEBUG_QUEST_KEY
from app.models import UserData


@pytest.fixture
def random_id():
    """ A random alphanumeric ID for various uses in tests """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


@pytest.fixture
def random_user():
    """ A random user for testing, does not write to database """
    user_id = "test_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )
    return User.from_source_id(Source.TEST, user_id)


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

    game = Game.new_from_fork(testing_user, fork_url)
    yield game


@pytest.fixture
def testing_quest(testing_game):
    """ A random quest for testing, cleans up afterwards """
    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)
    quest = QuestClass.from_game(testing_game)

    yield quest
