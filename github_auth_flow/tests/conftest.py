""" Setup for tests """

import os
import string
import random
import pytest
import requests

import firebase_admin
from firebase_admin import auth
from firebase_admin import firestore

from functions_framework import create_app  # type: ignore
from app.utils.models import UserData

FUNCTION_SOURCE = "app/main.py"
WEB_API_KEY = os.environ.get("WEB_API_KEY")
GH_TEST_TOKEN = os.environ.get("GH_TEST_TOKEN")


@pytest.fixture(scope="package")
def client():
    """ Test client """
    return create_app("github_auth_flow", FUNCTION_SOURCE).test_client()


@pytest.fixture(scope="package")
def firebase_app():
    """ The firebase app, used for tests and stuff """
    return firebase_admin.initialize_app(name="test")


@pytest.fixture(scope="package")
def firestore_client(firebase_app):
    """ The firebase app, used for tests and stuff """
    return firestore.client(app=firebase_app)


@pytest.fixture(scope="package")
def test_user(firebase_app, firestore_client):
    uid = "test_user_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )

    # create user
    yield auth.create_user(
        uid=uid,
        display_name="test_user",
        email="test_user@example.com",
        app=firebase_app,
    )

    # cleanup
    auth.delete_user(uid, app=firebase_app)
    firestore_client.collection("users").document(uid).delete()
    firestore_client.collection("system").document("stats").update(
        {"players": firestore.Increment(-1)}
    )


@pytest.fixture(scope="package")
def test_user_token(firebase_app, firestore_client, test_user):
    """ Create a new test user and get a login key """

    # create custom token
    token = auth.create_custom_token(test_user.uid, app=firebase_app).decode()

    # get ID token - Python Firebase Auth library doesn't have this function *shrug*
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={WEB_API_KEY}"
    res = requests.post(url, json={"token": token, "returnSecureToken": True})
    res.raise_for_status()

    return res.json()["idToken"]


@pytest.fixture
def test_user_data():
    """ Creates test user data """
    return UserData(
        profileImage="",
        name="Yuan Gao",
        handle="meseta",
        id="930832",
        accessToken=GH_TEST_TOKEN,
    ).dict()
