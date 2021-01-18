""" Setup for tests """

import os
import string
import random
import json
import pytest

import firebase_admin
from firebase_admin import firestore

from functions_framework import create_app  # type: ignore

FUNCTION_SOURCE = "app/main.py"


@pytest.fixture(scope="package")
def new_game_client():
    """ Test client for newgame"""
    return create_app("create_new_game", FUNCTION_SOURCE, "event").test_client()


@pytest.fixture(scope="package")
def firebase_app():
    """ The firebase app, used for tests and stuff """
    return firebase_admin.initialize_app(name="test")


@pytest.fixture(scope="package")
def firestore_client(firebase_app):
    """ The firebase app, used for tests and stuff """
    return firestore.client(app=firebase_app)
