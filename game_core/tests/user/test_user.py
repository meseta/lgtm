""" Tests for Game module """

import pytest
from app.user import User, NoUser, Source, find_user_by_source_id

# pylint: disable=redefined-outer-name
def test_bad_new():
    """ Errors caused by invaild init arguments """
    with pytest.raises(ValueError):
        User(None, "abc")

    with pytest.raises(ValueError):
        User(Source.TEST, "")

    with pytest.raises(ValueError):
        User(None, "")


def test_reference():
    """ Test creation of a hypothetical user"""
    user = User(Source.TEST, "0")
    assert user.key
    assert str(user)
    assert repr(user)


def test_not_find_by_source_id():
    """ Test failing to find a user by source ID """
    user = find_user_by_source_id(Source.TEST, "_user_does_not_exist_")
    assert user is NoUser


def test_find_by_source_id(testing_user):
    """ Test finding the user by source ID """
    user = find_user_by_source_id(testing_user.source, testing_user.user_id)
    assert isinstance(user, User)
