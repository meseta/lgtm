""" Setup for tests """

import os
import string
import random
import pytest
import requests

import firebase_admin
from firebase_admin import auth

from functions_framework import create_app  # type: ignore

FUNCTION_SOURCE = "app/main.py"
WEB_API_KEY = os.environ.get("WEB_API_KEY")

@pytest.fixture(scope="package")
def client():
    """ Test client """
    return create_app("github_auth_flow", FUNCTION_SOURCE).test_client()

@pytest.fixture(scope="package")
def firebase_app():
    """ The firebase app, used for tests and stuff """
    return firebase_admin.initialize_app(name="test")

@pytest.fixture(scope="package")
def test_user_token(firebase_app):
    """ Create a new test user and get a login key """

    # create user
    uid = "test_user_"+"".join([random.choice(string.ascii_letters) for _ in range(10)])
    user = auth.create_user(
        uid=uid,
        app=firebase_app
    )

    # create custom token
    token = auth.create_custom_token(user.uid, app=firebase_app).decode()

    # get ID token - Python Firebase Auth library doesn't have this function *shrug*
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={WEB_API_KEY}"
    res = requests.post(url, json={"token": token, "returnSecureToken": True})
    res.raise_for_status()
    
    yield res.json()["idToken"]

    # cleanup
    auth.delete_user(user.uid, app=firebase_app)

    