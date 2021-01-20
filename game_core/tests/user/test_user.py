""" Tests for Game module """

import pytest
from app.firebase_utils import db
from app.user import User, Source
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


def test_new(random_id):
    """ Test the creation of a new user """
    uid = "test_" + random_id

    # check doesn't exist before
    doc = db.collection("users").document(uid).get()
    assert not doc.exists

    # create user
    user_data = UserData(
        profileImage="", name="Test User", handle="test_user", id=uid, accessToken=""
    )
    user = User.new(uid, Source.TEST, user_data)
    assert user.uid == uid

    # check now exists
    doc = db.collection("users").document(uid).get()
    assert doc.exists

    # cleanup
    doc.reference.delete()


def test_second_creation(random_user):
    """ Test second creation doesn't error """
    uid = random_user.uid
    user_data = UserData(
        profileImage="", name="Test User", handle="test_user", id="0", accessToken=""
    )
    user = User.new(uid, Source.TEST, user_data)
    assert user.uid == uid


def test_not_found_by_source_id(random_user):
    """ Test failing to find a user by source ID """
    user = User.find_by_source_id(Source.TEST, "_user_does_not_exist_")
    assert user is None


def test_find_by_source_id(random_user):
    """ Test finding the user by source ID """
    user = User.find_by_source_id(random_user.source, random_user.user_id)
    assert user.uid == random_user.uid
