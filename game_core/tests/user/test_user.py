""" Tests for Game module """

import pytest
from app.firebase_utils import db
from app.user import User, NoUser, Source
from app.models import UserData

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
    """ Test creation of a user that is an unchecked reference """
    user = User.reference(Source.TEST, "0")
    assert user.key
    assert str(user)
    assert repr(user)


def test_second_creation(testing_user):
    """ Test second creation doesn't error """
    uid = testing_user.uid
    user_data = UserData(
        profileImage="", name="Test User", handle="test_user", id="0", accessToken=""
    )
    user = User.new(uid, Source.TEST, user_data)
    assert user.uid == uid


def test_fail_find_by_source_id():
    """ Test failing to find a user by source ID """
    user = User.find_by_source_id(Source.TEST, "_user_does_not_exist_")
    assert user is NoUser


def test_find_by_source_id(testing_user):
    """ Test finding the user by source ID """
    user = User.find_by_source_id(testing_user.source, testing_user.user_id)
    assert user.uid == testing_user.uid
