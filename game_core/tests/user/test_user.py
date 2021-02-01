""" Tests for Game module """

import pytest
from user import User, Source, NoUid
from orm import NoKey, OrmNotFound


def test_init():
    """ Test creation of a hypothetical user"""
    user = User.from_source_id(Source.TEST, "0")
    assert user.key
    assert str(user)
    assert repr(user)


def test_random_init():
    """ This isn't avlid flow, but we're testing it anyway """
    user = User(NoKey)
    user.delete()  # shouldn't do anything
    user.load()  # shouldn't do anything

    assert user.key is NoKey
    user.save()  # should save with new doc id
    assert user.key is not NoKey


def test_orm(testing_user):
    """ This actually tests an obscure path in the ORM """

    assert testing_user.parent is OrmNotFound


def test_not_from_by_source_id():
    """ Test failing to find a user by source ID """
    user = User.from_source_id(Source.TEST, "_user_does_not_exist_")
    assert not user.exists
    assert user.uid is NoUid


def test_from_source_id(testing_user):
    """ Test finding the user by source ID """

    # get user ID for searching from fixture
    user_id = testing_user.data.id

    # do search
    user = User.from_source_id(Source.TEST, user_id)
    assert user.exists
    assert user.uid == testing_user.uid


def test_second_creation(testing_user, testing_user_data):
    """ Testing creating user a second time """

    user = User.new_from_data(testing_user_data.id, Source.TEST, testing_user_data)
    assert user.key == testing_user.key
