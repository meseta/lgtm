""" Tests for main.py """

import copy
from firebase_admin import auth

# pylint: disable=redefined-outer-name
def test_unauthenticated(client):
    """ Test unauthenticated """
    res = client.post("/")
    assert res.status_code == 403

def test_user_invalid(client, firebase_app, test_user_token):
    """ Test when user is invalid """

    bad_data = {
        "foo": "bar",
        "moo": "cow",
    }
    res = client.post("/", headers={"Authorization": "Bearer "+test_user_token}, json=bad_data)
    assert res.status_code == 400


def test_github_invalid(client, firebase_app, test_user_token, test_user_data):
    """ Test when github token is invalid """

    test_user_data["accessToken"] = "foobar" # make access token bad
    res = client.post("/", headers={"Authorization": "Bearer "+test_user_token}, json=test_user_data)
    assert res.status_code == 400


def test_good_flow(client, firebase_app, test_user_token, test_user_data, test_user, firestore_client):
    """ Test a successful flow """

    res = client.post("/", headers={"Authorization": "Bearer "+test_user_token}, json=test_user_data)
    assert res.status_code == 200

    # check firestore
    doc = firestore_client.collection("users").document(test_user.uid).get()
    assert doc.exists
    assert doc.get("id") == test_user_data["id"]