""" Setup for tests """

import pytest
import string
import random

from app.firebase_utils import db
from app.user import User, Source
from app.models import UserData


@pytest.fixture
def random_id():
    """ A random alphanumeric ID for various uses in tests """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


@pytest.fixture(scope="package")
def random_user():
    """ A random user for testing, cleans up afterwards """
    uid = "test_" + "".join([random.choice(string.ascii_letters) for _ in range(10)])

    user_data = UserData(
        profileImage="", name="Test User", handle="test_user", id=uid, accessToken=""
    )

    user = User.new(uid, Source.TEST, user_data)
    yield user

    # cleanup
    db.collection("users").document(uid).delete()
