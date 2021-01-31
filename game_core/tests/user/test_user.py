""" Tests for Game module """

import pytest
from user import User, NoUser, Source

# pylint: disable=redefined-outer-name
def test_reference():
    """ Test creation of a hypothetical user"""
    user = User.from_source_id(Source.TEST, "0")
    assert user.key
    assert str(user)
    assert repr(user)


def test_not_find_by_source_id():
    """ Test failing to find a user by source ID """
    user = User.from_source_id(Source.TEST, "_user_does_not_exist_")
    assert not user.uid


def test_find_by_source_id(testing_user):
    """ Test finding the user by source ID """

    user_id = User.key_to_user_id(testing_user.key)
    user = User.from_source_id(Source.TEST, user_id)
    assert user.uid
    assert user.uid == testing_user.uid


def test_second_creation(testing_user, testing_user_data):
    """ Testing creating user a second time """

    user = User.new_from_data(testing_user_data.id, Source.TEST, testing_user_data)
    assert user.key == testing_user.key
