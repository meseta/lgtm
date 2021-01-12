""" Tests for main.py """

from firebase_admin import auth

# pylint: disable=redefined-outer-name
def test_unauthenticated(client):
    """ Test unauthenticated """
    res = client.post("/")
    assert res.status_code == 403

def test_main(client, firebase_app, test_user_token):
    """ Placeholder """

    res = client.post("/", headers={"Authorization": "Bearer "+test_user_token})
    assert res.status_code == 200