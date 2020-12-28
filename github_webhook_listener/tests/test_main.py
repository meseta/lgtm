""" Tests for main.py """

# pylint: disable=redefined-outer-name
def test_good_fork(client, good_fork):
    """ For a good fork that's working fine """

    res = client.post("/", headers=good_fork.headers, data=good_fork.payload)
    assert res.status_code == 200


def test_model_validation_fail(client, bad_fork):
    """ Test model validation failure with bad payload but correct signature for it"""

    res = client.post("/", headers=bad_fork.headers, data=bad_fork.payload)
    assert res.status_code == 400


def test_signature_fail(client, good_fork, bad_fork):
    """ Test signature validation failure with good payload but incorrect signature for it"""

    res = client.post("/", headers=bad_fork.headers, data=good_fork.payload)
    assert res.status_code == 403


def test_no_signature(client, good_fork):
    """ When signatures are not supplied """

    res = client.post(
        "/", headers={"Content-Type": "application/json"}, data=good_fork.payload
    )
    assert res.status_code == 403
