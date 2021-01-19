""" Setup for tests """

import pytest

import firebase_admin
from firebase_admin import firestore


@pytest.fixture(scope="package")
def firebase_app():
    """ The firebase app, used for tests and stuff """
    return firebase_admin.initialize_app(name="test")


@pytest.fixture(scope="package")
def firestore_client(firebase_app):
    """ The firebase app, used for tests and stuff """
    return firestore.client(app=firebase_app)
